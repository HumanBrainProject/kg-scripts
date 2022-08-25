from kg_core.kg import Client, Admin, kg
from kg_core.request import Stage, Pagination


class RemoveSpace(object):

    def __init__(self, kg_client: Client, kg_admin: Admin, properties: dict, simulate: bool):
        self.kg_client = kg_client
        self.kg_admin = kg_admin
        self._space_name: str = properties['spaceName']
        self._simulate: bool = simulate

    def remove_space(self):
        types = self.kg_client.types.list(space=self._space_name, stage=Stage.IN_PROGRESS)
        errors = False
        for t in types.items():
            instances = self.kg_client.instances.list(target_type=t.identifier, stage=Stage.IN_PROGRESS, pagination=Pagination(size=0)) # The only thing we're interested in is the total -> we therefore can set the size of the page to 0
            if not instances.error:
                if instances.total>0:
                    print(f"Type {t.identifier} in space {self._space_name} still contains {instances.total} instances - skipping.")
                    errors = True
                else:
                    if self._simulate:
                        print(f"Would remove type definition for {t.identifier}")
                    else:
                        error = self.kg_admin.remove_type_from_space(space=self._space_name, target_type=t.identifier)
                        if error:
                            print(f"Wasn't able to remove type {t.identifier} from space {self._space_name} - reason {error.code}")
                            errors = True
                        else:
                            print(f"Successfully removed type {t.identifier} from space {self._space_name}")
            else:
                print(f"Was not able to evaluate the number of instances of type {t.identifier} in space {self._space_name}")
                errors = True
        if errors:
            print("Was not able to remove all type definitions. Stopping.")
        else:
            if self._simulate:
                print(f"Would remove space definition for {self._space_name}")
            else:
                error = self.kg_admin.remove_space_definition(space=self._space_name)
                if error:
                    print(f"Wasn't able to remove the space specification for {self._space_name} - reason {error.code}")


def run(properties: dict, kg_client: Client, kg_admin: Admin, simulate:bool):
    RemoveSpace(kg_client, kg_admin, properties, simulate).remove_space()


if __name__ == '__main__':
    # endpoint = "core.kg.ebrains.eu"
    endpoint = "core.kg-ppd.ebrains.eu"
    simulate = True
    run({"spaceName": "collab-ebrains-workflows"}, kg(endpoint).build(), kg(endpoint).build_admin(), simulate)
