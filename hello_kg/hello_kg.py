from kg_core.kg import KGv3


class HelloKG():
    def __init__(self, kg:KGv3):
        self.kg = kg

    def say_hello(self, properties, simulate:bool):
        me = self.kg.me().data()
        if simulate:
            print(f"You are in simulation mode. If you would run this script, it would say \"Hello {properties['name']} - aka {me['http://schema.org/name']}! Welcome to the KG automation! I'm going to talk to {self.kg.endpoint}\"")
        else:
            print(f"Hello {properties['name']} - aka {me['http://schema.org/name']}! Welcome to the KG automation! I'm going to talk to {self.kg.endpoint}")


def run(properties:dict, kg:KGv3):
    HelloKG(kg).say_hello(properties, False)


def simulate(properties:dict, kg:KGv3):
    HelloKG(kg).say_hello(properties, True)