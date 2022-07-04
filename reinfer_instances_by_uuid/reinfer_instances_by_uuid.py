import os
from typing import List

from kg_core.kg import KGv3
from kg_core.models import Stage, ResponseConfiguration, Pagination
from kg_core.oauth import SimpleToken

class ReinferInstancesByUUID(object):

    def __init__(self, kg: KGv3, properties: dict, simulate: bool):
        self.kg = kg
        self._uuids: List[str] = properties['uuids']
        self._simulate: bool = simulate

    def reinfer(self):
        instances = self.kg.get_instances_by_ids(Stage.IN_PROGRESS, self._uuids)
        while instances and instances.data():
            for instance_key, instance_value in instances.data().items():
                if "data" in instance_value and instance_value["data"]:
                    instance_data = instance_value["data"]
                    if "https://core.kg.ebrains.eu/vocab/meta/space" in instance_data and instance_data["https://core.kg.ebrains.eu/vocab/meta/space"]:
                        space = instance_data["https://core.kg.ebrains.eu/vocab/meta/space"]
                        if self._simulate:
                            print(f"Will try to reinfer the instance {instance_data['@id']} in space {space}")
                        else:
                            result = self.kg.post(path=f"/spaces/{space}/inference", payload={}, params={"identifier": instance_data['@id']})
                            if result.is_successful():
                                print(f"Successfully reinferred {instance_data['@id']} in space {space}")
                            else:
                                print(f"Was not able to reinfer {instance_data['@id']} in space {space}")
                    else:
                        print(f"Was not able to determine the space of {instance_key}")
                else:
                    print(f"Was not able to read instance {instance_key}")
            instances = self.kg.next_page(instances)


def run(properties: dict, kg: KGv3):
    ReinferInstancesByUUID(kg, properties, False).reinfer()


def simulate(properties: dict, kg: KGv3):
    ReinferInstancesByUUID(kg, properties, True).reinfer()


if __name__ == '__main__':
    ReinferInstancesByUUID(KGv3("core.kg-ppd.ebrains.eu", token_handler=SimpleToken(os.getenv("KG_TOKEN"))), {"uuids": [ "3ba258ca-0ea6-42a8-a744-d1617bf83bd0"]}, False).reinfer()
