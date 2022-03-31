from typing import List

from kg_core.kg import KGv3
from kg_core.oauth import ClientCredentials


class CreateCollabSpace(object):

    def __init__(self, kg: KGv3, properties: dict, simulate: bool):
        self.kg = kg
        self._collab_name: bool = properties['collabName']
        self._apply_types_from_space: List[str] = properties["applyTypesFromSpace"]
        self._simulate: bool = simulate

    def create_collab_space(self):
        result = self.kg.put(path=f"/spaces/collab-{self._collab_name}/specification", payload={}, params={"autorelease": False, "clientSpace":False, "deferCache": False})
        print(result)


def run(properties: dict, kg: KGv3):
    CreateCollabSpace(kg, properties, False).create_collab_space()


def simulate(properties: dict, kg: KGv3):
    CreateCollabSpace(kg, properties, True).create_collab_space()