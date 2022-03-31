from typing import List

from kg_core.kg import KGv3
from kg_core.models import Stage
from kg_core.oauth import ClientCredentials


class CreateCollabSpace(object):

    def __init__(self, kg: KGv3, properties: dict, simulate: bool):
        self.kg = kg
        self._space_name: str = f"collab-{properties['collabName']}"
        self._types_from_space = properties["applyTypesFromSpace"] if "applyTypesFromSpace" in properties else None
        self._simulate: bool = simulate

    def _apply_types_from_space(self):
        if not self._types_from_space:
            print("No types applied from another space")
        else:
            result = self.kg.types(Stage.IN_PROGRESS, self._types_from_space)
            if result.is_successful():
                for t in result.data():
                    type_name = t['http://schema.org/identifier']
                    if self._simulate:
                        print(f"Would attach type {type_name} to space {self._space_name}")
                    else:
                        result = self.kg.put(path=f"/spaces/{self._space_name}/types", payload={}, params={"type": type_name})
                        if result.status_code == 200:
                            print(f"Successfully attached the type {type_name} to space {self._space_name}")
                        else:
                            print(f"Was not able to attach the type {type_name} to space {self._space_name} - reason {result.status_code}")
            else:
                print(f"Wasn't able to fetch the types from space {self._space_name}")

    def create_collab_space(self):
        if self._simulate:
            print(f"Would try to create the collab space for {self._space_name}")
            self._apply_types_from_space()
        else:
            result = self.kg.put(path=f"/spaces/{self._space_name}/specification", payload={}, params={"autorelease": False, "clientSpace":False, "deferCache": False}).status_code
            if result == 200:
                print(f"Successfully created collab space for {self._space_name}")
                self._apply_types_from_space()
            else:
                print(f"Was not able to create space - {result}")


def run(properties: dict, kg: KGv3):
    CreateCollabSpace(kg, properties, False).create_collab_space()


def simulate(properties: dict, kg: KGv3):
    CreateCollabSpace(kg, properties, True).create_collab_space()