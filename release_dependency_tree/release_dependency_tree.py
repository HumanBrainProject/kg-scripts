import uuid
from typing import List
from uuid import UUID

from kg_core.kg import Client, Admin, kg
from kg_core.request import ReleaseTreeScope, Stage
from kg_core.response import Result, Scope, ResultsById, ReleaseStatus


class ReleaseDependencyTree(object):

    def __init__(self, kg_client: Client, kg_admin: Admin, properties: dict, simulate: bool):
        self.kg_client = kg_client
        self.kg_admin = kg_admin
        self._release_ebrains_dois: bool = properties['releaseEbrainsDOIs']
        self._root_documents: List[str] = properties["rootDocuments"]
        self._simulate: bool = simulate

    def _get_ids_of_tree(self, tree:Scope, collector: set):
        if tree.uuid:
            exclude = False
            if tree.types:
                type_list = tree.types
                if not type(type_list) == list:
                    type_list = [type_list]
                if not self._release_ebrains_dois and "https://openminds.ebrains.eu/core/DOI" in type_list and "doi.org/10.25493" in tree.label:
                    print(f"Exclude {tree.uuid} because this is an EBRAINS DOI")
                    exclude = True
            if not exclude:
                collector.add(str(tree.uuid))
        if tree.children:
            for c in tree.children:
                self._get_ids_of_tree(c, collector)

    def release_all_instances_by_type(self, target_type, space):
        instances = self.kg_client.instances.list(target_type=target_type, stage=Stage.IN_PROGRESS, space=space)
        for i in instances.items():
            self.release_scope_tree(i.uuid)

    def release_scope_tree(self, uuid:UUID):
        print(f"Releasing scope tree for {uuid}")
        scope_tree: Result[Scope] = self.kg_client.instances.get_scope(instance_id=uuid, apply_restrictions=True, stage=Stage.IN_PROGRESS)
        id_collector = set()
        id_collector.add(str(uuid))
        if scope_tree.data:
            self._get_ids_of_tree(scope_tree.data, id_collector)
            status: ResultsById[ReleaseStatus] = self.kg_client.instances.get_release_status_by_ids(list(id_collector), ReleaseTreeScope.TOP_INSTANCE_ONLY)
            if status.data:
                for k in status.data.keys():
                    value: Result[ReleaseStatus] = status.data[k]
                    if not value.data or value.data != ReleaseStatus.RELEASED:
                        if self._simulate:
                            print(f"Would release {k}")
                        else:
                            release_result = self.kg_client.instances.release(instance_id=k)
                            if release_result.is_successful():
                                print(f"Successfully released {k}")
                            else:
                                print(f"Was not able to release {k} - {release_result.error()}")
                    elif value.data and value.data == ReleaseStatus.RELEASED:
                        print(f"Skipping {k} because it's already released")
        else:
            print(f"No release tree found for id {id}")

    def release_dependency_tree(self):
        for root_document in self._root_documents:
            self.release_scope_tree(uuid.UUID(root_document))


def run(properties: dict, kg_client: Client, kg_admin: Admin, simulate:bool):
    ReleaseDependencyTree(kg_client, kg_admin, properties, simulate).release_dependency_tree()


if __name__ == '__main__':
    # endpoint = "core.kg.ebrains.eu"
    endpoint = "core.kg-ppd.ebrains.eu"
    simulate = True
    run( { "rootDocuments": [ "07554ebd-95a2-46f0-8065-d961d56ce098"], "releaseEbrainsDOIs": False}, kg(endpoint).build(), kg(endpoint).build_admin(), simulate)
