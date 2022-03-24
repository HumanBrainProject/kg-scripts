from kg_core.kg import KGv3


class HelloKG():
    def __init__(self, kg:KGv3):
        self.kg = kg
        pass

    def say_hello(self, properties):
        me = self.kg.me().data()
        print(f"Hello {properties['name']} - aka {me['http://schema.org/name']}! Welcome to the KG automation! I'm going to talk to {self.kg.endpoint}")


def run(properties:dict, kg:KGv3):
    HelloKG(kg).say_hello(properties)