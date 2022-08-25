import json
import re

from kg_core.kg import Client, Admin, kg
from kg_core.request import Stage, Pagination


class AttachInstancesByPattern():

    def __init__(self, kg_client: Client, kg_admin: Admin, properties: dict, simulate: bool):
        self.kg_client = kg_client
        self.kg_admin = kg_admin
        self.target_instance = properties["target"]["instanceUUID"]
        self.target_property = properties["target"]["property"]
        self.source_space = properties["source"]["space"]
        self.source_type = properties["source"]["type"]
        self.source_filter_property = properties["source"]["filterProperty"]
        self.source_filter_pattern = properties["source"]["filterPattern"]
        self.source_range_from = properties["source"]["range"]["from"]
        self.source_range_to = properties["source"]["range"]["to"]
        self._simulate: bool = simulate

    def attach_instances_by_pattern(self):
        if type(self.source_range_from) != type(self.source_range_to):
            raise ValueError("You've specified a range with different value types. This is not allowed!")
        instance = self.kg_client.instances.get_by_id(self.target_instance, stage=Stage.IN_PROGRESS)
        if instance.error:
            raise ValueError(f"Was not able to read the instance {self.target_instance} - {instance.error}")
        new_value = []
        if self.target_property in instance.data and instance.data[self.target_property]:
            new_value = instance.data[self.target_property]
        print("Looking for potential instances to be matched...")
        target_instances = self.kg_client.instances.list(target_type=self.source_type, space=self.source_space, stage=Stage.IN_PROGRESS, pagination=Pagination(size=1000, return_total_results=False))
        has_new_values = False
        for instance in target_instances.items():
            filter_value = instance[self.source_filter_property] if self.source_filter_property in instance else None
            if filter_value:
                matches = re.findall(self.source_filter_pattern, filter_value)
                for match in matches:
                    casted_match = type(self.source_range_from)(match)
                    if self.source_range_from <= casted_match <= self.source_range_to:
                        print(f"Valid property match for attaching found: {filter_value}")
                        link = {"@id": instance.instance_id}
                        if link not in new_value:
                            has_new_values = True
                            new_value.append(link)
        if not has_new_values:
            print("All items already belong to the instance - no need to do an update")
        else:
            if self._simulate:
                print(f"I would update the property {self.target_property} of instance {self.target_instance} to the value {json.dumps(new_value, indent=4)}")
            else:
                result = self.kg_client.instances.contribute_to_partial_replacement(payload = {
                    self.target_property: new_value
                }, instance_id=self.target_instance)
                if result.error:
                    print(f"Was not able to update the instance {self.target_instance} - {result.error}")
                else:
                    print(f"Successfully updated the property {self.target_property} of the instance {self.target_instance} to {json.dumps(new_value, indent=4)}")


def run(properties: dict, kg_client: Client, kg_admin: Admin, simulate: bool):
    AttachInstancesByPattern(kg_client, kg_admin, properties, simulate).attach_instances_by_pattern()


if __name__ == '__main__':
    # endpoint = "core.kg.ebrains.eu"
    endpoint = "core.kg-ppd.ebrains.eu"
    simulate = True
    with open("parameter_template.json", "r") as example:
        payload = json.load(example)
    run(payload, kg(endpoint).build(), kg(endpoint).build_admin(), simulate)