from typing import List

from kg_core.kg import KGv3
from kg_core.models import Stage


class ReleaseDependencyTree(object):

    def __init__(self, kg: KGv3, properties: dict, simulate: bool):
        self.kg = kg
        self._release_ebrains_dois: bool = properties['releaseEbrainsDOIs']
        self._root_documents: List[str] = properties["rootDocuments"]
        self._simulate: bool = simulate

    def _get_ids_of_tree(self, tree, collector: set):
        if "id" in tree:
            exclude = False
            if "types" in tree:
                type_list = tree["types"]
                if not type(type_list):
                    type_list = [type_list]
                if not self._release_ebrains_dois and "https://openminds.ebrains.eu/core/DOI" in type_list and "doi.org/10.25493" in tree["label"]:
                    print(f"Exclude {tree['id']} because this is an EBRAINS DOI")
                    exclude = True
            if not exclude:
                collector.add(tree["id"])
        if "children" in tree and tree["children"]:
            for c in tree["children"]:
                self._get_ids_of_tree(c, collector)

    def release_all_instances_by_type(self, type, space):
        instances = self.kg.get_instances(Stage.IN_PROGRESS, type, space)
        while instances:
            if instances.data():
                for i in instances.data():
                    self.release_scope_tree(str(KGv3.uuid_from_absolute_id(i["@id"])))
            instances = self.kg.next_page(instances)

    def release_scope_tree(self, id):
        print(f"Releasing scope tree for {id}")
        scope_tree = self.kg.get(f"/instances/{id}/scope", {"stage": Stage.IN_PROGRESS, "applyRestrictions": True})
        data = scope_tree.data()
        id_collector = set()
        id_collector.add(id)
        if data:
            self._get_ids_of_tree(data, id_collector)
            status = self.kg.post(f"/instancesByIds/release/status", payload=list(id_collector), params={"releaseTreeScope": "TOP_INSTANCE_ONLY"})
            if status.is_successful():
                for k in status.data().keys():
                    v = status.data()[k]
                    if "data" not in v or v["data"] != "RELEASED":
                        if self._simulate:
                            print(f"Would release {k}")
                        else:
                            release_result = self.kg.put(f"/instances/{k}/release", {}, {})
                            if release_result.is_successful():
                                print(f"Successfully released {k}")
                            else:
                                print(f"Was not able to release {k} - {release_result.error()}")
                    elif v["data"] == "RELEASED":
                        print(f"Skipping {k} because it's already released")
        else:
            print(f"No release tree found for id {id}")

    def release_dependency_tree(self):
        for root_document in self._root_documents:
            self.release_scope_tree(root_document)


def run(properties: dict, kg: KGv3):
    ReleaseDependencyTree(kg, properties, False).release_dependency_tree()


def simulate(properties: dict, kg: KGv3):
    ReleaseDependencyTree(kg, properties, True).release_dependency_tree()
