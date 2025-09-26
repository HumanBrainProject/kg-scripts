from kg_core.kg import Client, Admin, kg
from kg_core.request import Stage


class CreateSpace(object):

    def __init__(self, kg_client: Client, kg_admin: Admin, properties: dict, simulate: bool):
        self.kg_client = kg_client
        self.kg_admin = kg_admin
        self._space_name: str = properties['targetName']
        self._types_from_space = properties["applyTypesFromSpace"] if "applyTypesFromSpace" in properties else None
        self._simulate: bool = simulate

    def _apply_types_from_space(self):
        if not self._types_from_space:
            print("No types applied from another space")
        else:
            result = self.kg_client.types.list(stage=Stage.IN_PROGRESS, space=self._types_from_space)
            for t in result.items():
                if self._simulate:
                    print(f"Would attach type {t.identifier} to space {self._space_name}")
                else:
                    error = self.kg_admin.assign_type_to_space(space=self._space_name, target_type=t.identifier)
                    if error:
                        print(f"Was not able to attach the type {t.identifier} to space {self._space_name} - reason {result.status_code}")
                    else:
                        print(f"Successfully attached the type {t.identifier} to space {self._space_name}")

    def create_space(self):
        if self._simulate:
            print(f"Would try to create a space {self._space_name}")
            self._apply_types_from_space()
        else:
            error = self.kg_admin.create_space_definition(space=self._space_name)
            if error:
                print(f"Was not able to create space - {error}")
            else:
                print(f"Successfully created space for {self._space_name}")
                self._apply_types_from_space()


def run(properties: dict, kg_client: Client, kg_admin: Admin, simulate: bool):
    CreateSpace(kg_client, kg_admin, properties, simulate).create_space()


if __name__ == '__main__':
    # endpoint = "core.kg.ebrains.eu"
    endpoint = "core.kg-ppd.ebrains.eu"
    simulate = True
    run({ "targetName": "foobar", "applyTypesFromSpace": "collab-software-curation" }, kg(endpoint).build(), kg(endpoint).build_admin(), simulate)
