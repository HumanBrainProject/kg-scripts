from kg_core.kg import KGv3
from kg_core.models import Stage


class RemoveSpace(object):

    def __init__(self, kg: KGv3, properties: dict, simulate: bool):
        self.kg = kg
        self._space_name: str = properties['spaceName']
        self._simulate: bool = simulate

    def remove_space(self):
        instances = self.kg.get_instances(Stage.IN_PROGRESS, None, self._space_name)
        if instances.is_successful():
            if instances.total()>0:
                print(f"Can not remove space {self._space_name} because it still contains {instances.total()} instances - please (re)move them first")
            else:
                types = self.kg.types(Stage.IN_PROGRESS, self._space_name)
                if types.is_successful():
                    errors = False
                    for t in types.data():
                        type_name = t['http://schema.org/identifier']
                        if self._simulate:
                            print(f"Would remove type definition for {type_name}")
                        else:
                            type_removal = self.kg.delete(path=f'/spaces/{self._space_name}/types', params={"type": type_name})
                            if type_removal.status_code==200:
                                print(f"Successfully removed type {type_name} from space {self._space_name}")
                            else:
                                print(f"Wasn't able to remove type {type_name} from space {self._space_name} - reason {type_removal.status_code}")
                                errors = True
                        if errors:
                            print("Was not able to remove all type definitions. Stopping.")
                        else:
                            if self._simulate:
                                print(f"Would remove space definition for {self._space_name}")
                            else:
                                space_spec = self.kg.delete(path=f'/spaces/{self._space_name}/specification', params={})
                                if space_spec.status_code == 200:
                                    print(f"Successfully removed space specification for {self._space_name}")
                                else:
                                    print(f"Wasn't able to remove the space specification for {self._space_name} - reason {space_spec.status_code}")
                else:
                    print(f"Wasn't able to find the type information for the space {self._space_name}")
        else:
            print("Wasn't able to validate the number of instances in the space remaining")


def run(properties: dict, kg: KGv3):
    RemoveSpace(kg, properties, False).remove_space()


def simulate(properties: dict, kg: KGv3):
    RemoveSpace(kg, properties, True).remove_space()