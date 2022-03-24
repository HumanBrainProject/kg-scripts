class HelloKG():
    def __init__(self):
        pass

    def say_hello(self, properties):
        print(f"Hello {properties['name']}! Welcome to the KG automation!")


def run(properties:dict, kg:KGv3):
    HelloKG().say_hello(properties)
