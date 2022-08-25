from kg_core.kg import Client, Admin, kg
from kg_core.response import User


class HelloKG():

    def __init__(self, kg_client: Client, kg_admin: Admin, properties: dict, simulate: bool):
        self.kg_client = kg_client
        self.kg_admin = kg_admin
        self.name = properties["name"]
        self._simulate: bool = simulate

    def say_hello(self):
        me: User = self.kg_client.users.my_info().data
        if self._simulate:
            print(f"You are in simulation mode. If you would run this script, it would say \"Hello {self.name} - aka {me.name}! Welcome to the KG automation!")
        else:
            print(f"Hello {self.name} - aka {me.name}! Welcome to the KG automation! ")


def run(properties: dict, kg_client: Client, kg_admin: Admin, simulate: bool):
    HelloKG(kg_client, kg_admin, properties, simulate).say_hello()


if __name__ == '__main__':
    # endpoint = "core.kg.ebrains.eu"
    endpoint = "core.kg-ppd.ebrains.eu"
    simulate = True
    run( { "name": "foobar"}, kg(endpoint).build(), kg(endpoint).build_admin(), simulate)