from kg_core.kg import KGv3
from kg_core.models import Stage, ResponseConfiguration, Pagination


class ReinferInstancesOfType(object):

    def __init__(self, kg: KGv3, properties: dict, simulate: bool):
        self.kg = kg
        self._space_name: str = properties['spaceName']
        self._type_name: str = properties['typeName']
        self._simulate: bool = simulate

    def reinfer(self):
        instances = self.kg.get_instances(Stage.IN_PROGRESS, self._type_name, self._space_name)
        while instances and instances.data():
            for instance in instances.data():
                if self._simulate:
                    print(f"Will try to reinfer the instance {instance['@id']}")
                else:
                    result = self.kg.post(path=f"/spaces/{self._space_name}/inference", payload={}, params={"identifier": instance['@id']})
                    if result.is_successful():
                        print(f"Successfully reinferred {instance['@id']}")
                    else:
                        print(f"Was not able to reinfer {instance['@id']}")
            instances = self.kg.next_page(instances)


def run(properties: dict, kg: KGv3):
    ReinferInstancesOfType(kg, properties, False).reinfer()


def simulate(properties: dict, kg: KGv3):
    ReinferInstancesOfType(kg, properties, True).reinfer()
