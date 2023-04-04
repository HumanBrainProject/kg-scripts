from kg_core.kg import  Admin, Client, kg
from kg_core.request import Stage, Pagination


class ReinferInstancesOfType(object):

    def __init__(self, kg_client: Client, kg_admin: Admin, properties: dict, simulate: bool):
        self.kg_client = kg_client
        self.kg_admin = kg_admin
        self._space_name: str = properties['spaceName']
        self._type_name: str = properties['typeName'] if "typeName" in properties else None
        self._simulate: bool = simulate

    def reinfer(self):
        if self._type_name:
            self._do_reinference(self._type_name)
        else:
            for type in self.kg_client.types.list(self._space_name, stage=Stage.IN_PROGRESS).items():
                if type.identifier:
                    self._do_reinference(type.identifier)

    def _do_reinference(self, type_name:str):
        print(f"Reinferring type {type_name}")
        instances = self.kg_client.instances.list(target_type=type_name, stage=Stage.IN_PROGRESS, space=self._space_name, pagination=Pagination(size=200))
        for instance in instances.items():
            if self._simulate:
                print(f"Will try to reinfer the instance {instance['@id']}")
            else:
                error = self.kg_admin.trigger_inference(space = self._space_name, identifier=instance.instance_id)
                if error:
                    print(f"Was not able to reinfer {instance.instance_id}")
                else:
                    print(f"Successfully reinferred {instance.instance_id}")


def run(properties: dict, kg_client: Client, kg_admin: Admin, simulate:bool):
    ReinferInstancesOfType(kg_client, kg_admin, properties, simulate).reinfer()


if __name__ == '__main__':
    # endpoint = "core.kg.ebrains.eu"
    endpoint = "core.kg-ppd.ebrains.eu"
    simulate = True
    run( { "spaceName": "common", "typeName": "https://openminds.ebrains.eu/core/Person" }, kg(endpoint).build(), kg(endpoint).build_admin(), simulate)
