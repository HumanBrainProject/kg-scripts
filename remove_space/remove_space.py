from kg_core.kg import KGv3
from kg_core.models import Stage, ResponseConfiguration, Pagination


class RemoveSpace(object):

    def __init__(self, kg: KGv3, properties: dict, simulate: bool):
        self.kg = kg
        self._space_name: str = properties['spaceName']
        self._simulate: bool = simulate

    def remove_space(self):
        types = self.kg.types(Stage.IN_PROGRESS, self._space_name)
        if types.is_successful():
            errors = False
            for t in types.data():
                type_name = t['http://schema.org/identifier']
                instances = self.kg.get_instances(Stage.IN_PROGRESS, type_name, self._space_name, pagination=Pagination(start_from=0, size=0))
                if instances.is_successful():
                    if instances.total()>0:
                        print(f"Type {type_name} in space {self._space_name} still contains {instances.total()} instances - skipping.")
                        errors = True
                    else:
                        if self._simulate:
                            print(f"Would remove type definition for {type_name}")
                        else:
                            type_removal = self.kg.delete(path=f'/spaces/{self._space_name}/types', params={"type": type_name})
                            if type_removal.status_code == 200:
                                print(f"Successfully removed type {type_name} from space {self._space_name}")
                            else:
                                print(f"Wasn't able to remove type {type_name} from space {self._space_name} - reason {type_removal.status_code}")
                                errors = True
                else:
                    print(f"Was not able to evaluate the number of instances of type {type_name} in space {self._space_name}")
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


def run(properties: dict, kg: KGv3):
    RemoveSpace(kg, properties, False).remove_space()


def simulate(properties: dict, kg: KGv3):
    RemoveSpace(kg, properties, True).remove_space()
