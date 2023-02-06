from uuid import UUID
import re

from kg_core.kg import Admin, Client, kg
from kg_core.request import Stage, Pagination

class TestFileStructurePattern(object):

    def __init__(self, kg_client: Client, kg_admin: Admin, properties: dict, simulate: bool):
        self.kg_client = kg_client
        self.kg_admin = kg_admin
        self._fileRepositoryUUID: UUID = properties['fileRepositoryUUID']
        self._filePathPattern: str = properties['filePathPattern']
        self._simulate: bool = simulate

    def test(self):
        page = self.kg_client.instances.get_incoming_links(self._fileRepositoryUUID, "https://openminds.ebrains.eu/vocab/fileRepository", "https://openminds.ebrains.eu/core/File", stage=Stage.IN_PROGRESS, pagination=Pagination(return_total_results=False))
        bundles = {}
        while page:
            ids = [str(i.uuid) for i in page.data]
            full_instances = self.kg_client.instances.get_by_ids(ids, stage=Stage.IN_PROGRESS)
            if full_instances.data:
                for k, f in full_instances.data.items():
                    if f.data:
                        iri = f.data["https://openminds.ebrains.eu/vocab/IRI"]
                        match = re.match(self._filePathPattern, iri)
                        if match:
                            bundle_name = " ".join([i for i in list(match.groups()) if i]).strip()
                            if bundle_name:
                                if bundle_name not in bundles:
                                    bundles[bundle_name] = []
                                bundles[bundle_name].append(iri)
            page = page.next_page()

        if bundles:
            print("The regular expression is going to create the following file bundles:")
            for b in sorted(bundles.keys()):
                print(f"{b}:")
                for f in sorted(bundles[b]):
                    print(f"   {f}")
        else:
            print("No file bundles would be created with the given logic")


def run(properties: dict, kg_client: Client, kg_admin: Admin, simulate: bool):
    TestFileStructurePattern(kg_client, kg_admin, properties, simulate).test()


if __name__ == '__main__':
    # endpoint = "core.kg.ebrains.eu"
    endpoint = "core.kg-int.ebrains.eu"
    simulate = True
    run({
        "fileRepositoryUUID": "05542a24-d03a-4d09-b0fc-8b665981cc70",
        "filePathPattern": ".+\\/(sIPSCs\\/Sub[1-3]{1}\\/Samp1)\\/.+"
    }, kg(endpoint).build(), kg(endpoint).build_admin(), simulate)
