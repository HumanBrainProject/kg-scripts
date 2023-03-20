import json
from uuid import UUID
import re

from kg_core.kg import Admin, Client, kg
from kg_core.request import Stage, Pagination, ReleaseTreeScope
from kg_core.response import ReleaseStatus


class FindChangedInstances(object):

    def __init__(self, kg_client: Client,  properties: dict):
        self.kg_client = kg_client
        self._type: UUID = properties['type']

    def test(self):
        result = self.kg_client.instances.list(self._type)
        has_changed = []
        while result and result.data:
            id_list = [str(f.uuid) for f in result.data]
            release_status = self.kg_client.instances.get_release_status_by_ids(id_list, ReleaseTreeScope.TOP_INSTANCE_ONLY)
            if release_status.data:
                for k, v in release_status.data.items():
                    if v.data and v.data == ReleaseStatus.HAS_CHANGED:
                        has_changed.append(k)
            result = result.next_page()
        print(f"Instances in HAS_CHANGED state: \n{json.dumps(has_changed, indent=4)}")


def run(properties: dict, kg_client: Client, kg_admin: Admin, simulate: bool):
    FindChangedInstances(kg_client, properties).test()


if __name__ == '__main__':
    endpoint = "core.kg.ebrains.eu"
    #endpoint = "core.kg-int.ebrains.eu"
    simulate = True
    run({
        "type": "https://openminds.ebrains.eu/core/DatasetVersion"
    }, kg(endpoint).build(), kg(endpoint).build_admin(), simulate)
