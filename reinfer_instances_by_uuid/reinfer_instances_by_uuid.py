from typing import List

from kg_core.kg import Admin, Client, kg
from kg_core.request import Stage
from kg_core.response import Instance, ResultsById, Result


class ReinferInstancesByUUID(object):

    def __init__(self, kg_client: Client, kg_admin: Admin, properties: dict, simulate: bool):
        self.kg_client = kg_client
        self.kg_admin = kg_admin
        self._uuids: List[str] = properties['uuids']
        self._simulate: bool = simulate

    def reinfer(self):
        instances: ResultsById[Instance] = self.kg_client.instances.get_by_ids(payload=self._uuids, stage=Stage.IN_PROGRESS)
        if instances.data:
            instance_keys = list(instances.data.keys())
            instance_keys.sort()
            for instance_key in instance_keys:
                instance:Result[Instance] = instances.data[instance_key]
                if instance.data:
                    instance_data:Instance = instance.data
                    if "https://core.kg.ebrains.eu/vocab/meta/space" in instance_data and instance_data["https://core.kg.ebrains.eu/vocab/meta/space"]:
                        space = instance_data["https://core.kg.ebrains.eu/vocab/meta/space"]
                        if self._simulate:
                            print(f"Will try to reinfer the instance {instance_data['@id']} in space {space}")
                        else:
                            error = self.kg_admin.trigger_inference(space=space, identifier=instance_data.instance_id)
                            if error:
                                print(f"Was not able to reinfer {instance_data.instance_id} in space {space}")
                            else:
                                print(f"Successfully reinferred {instance_data.instance_id} in space {space}")
                    else:
                        print(f"Was not able to determine the space of {instance_key}")
                else:
                    print(f"Was not able to read instance {instance_key}")


def run(properties: dict, kg_client: Client, kg_admin: Admin, simulate:bool):
    ReinferInstancesByUUID(kg_client, kg_admin, properties, simulate).reinfer()


if __name__ == '__main__':
    # endpoint = "core.kg.ebrains.eu"
    endpoint = "core.kg-ppd.ebrains.eu"
    simulate = True
    run( {"uuids": [ "3ba258ca-0ea6-42a8-a744-d1617bf83bd0"]}, kg(endpoint).build(), kg(endpoint).build_admin(), simulate)
