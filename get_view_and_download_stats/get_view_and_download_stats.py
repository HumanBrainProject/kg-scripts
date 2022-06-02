from typing import List

from kg_core.kg import KGv3
from kg_core.models import Stage
from kg_core.oauth import SimpleToken
import os


class GetViewAndDownloadStats(object):

    def __init__(self, kg: KGv3, properties: dict, simulate: bool):
        self.kg = kg
        self._simulate: bool = simulate
        self._filter_type = properties["filterType"]
        self._query = {
            "@context": {
                "@vocab": "https://core.kg.ebrains.eu/vocab/query/",
                "query": "https://schema.hbp.eu/myQuery/",
                "propertyName": {
                    "@id": "propertyName",
                    "@type": "@id"
                },
                "path": {
                    "@id": "path",
                    "@type": "@id"
                }
            },
            "meta": {
                "type": "https://core.kg.ebrains.eu/metrics/search/Metric",
                "responseVocab": "https://schema.hbp.eu/myQuery/"
            },
            "structure": [
                {
                    "propertyName": "query:metricOf",
                    "path": "https://core.kg.ebrains.eu/vocab/metricOf",
                    "required": True,
                    "singleValue": "FIRST",
                    "structure": [
                        {
                            "propertyName": "query:id",
                            "path": "@id"
                        },
                        {
                            "propertyName": "query:type",
                            "path": "@type"
                        }
                    ]
                },
                {
                    "propertyName": "query:allTimeViews",
                    "path": "https://core.kg.ebrains.eu/vocab/allTimeViews"
                },
                {
                    "propertyName": "query:allTimeDownloads",
                    "path": "https://core.kg.ebrains.eu/vocab/allTimeDownloads"
                },
                {
                    "propertyName": "query:last30daysDownloads",
                    "path": "https://core.kg.ebrains.eu/vocab/last30daysDownloads"
                },
                {
                    "propertyName": "query:last30daysViews",
                    "path": "https://core.kg.ebrains.eu/vocab/last30daysViews"
                }
            ]
        }

    def stats(self):
        instances = self.kg.queries(self._query, Stage.IN_PROGRESS)
        collect = []
        while instances and instances.data():
            collect.extend(instances.data())
            instances = self.kg.next_page(instances)
        if self._filter_type:
            collect = list(filter(lambda c: self._filter_type in c['metricOf']['type'], collect))
        self._aggregate(collect, "allTimeViews")
        self._aggregate(collect, "allTimeDownloads")
        self._aggregate(collect, "last30daysViews")
        self._aggregate(collect, "last30daysDownloads")

    def _aggregate(self, full_list:List[dict], sort_by:str):
        sorted_list = sorted(full_list, key=lambda d: d[sort_by], reverse=True)
        top_ten = sorted_list[0:10]
        ranges = [0, 10, 20, 50, 100, 150, 200, 300, 400, 500, 750, 1000, 1500, 2000, 5000, 10000]
        ranges.reverse()
        range_map = {"0": []}
        for i in full_list:
            uuid = self.kg.uuid_from_absolute_id(i['metricOf']['id'])
            if i[sort_by] == 0:
                range_map["0"].append(uuid)
            else:
                for range in ranges:
                    if i[sort_by] > range:
                        range_key = f">{range}"
                        if not range_key in range_map:
                            range_map[range_key] = []
                        range_map[range_key].append(uuid)
                        break
        print("************")
        print(sort_by)
        print("************")
        print("Top ten:")
        for i in top_ten:
            uuid = self.kg.uuid_from_absolute_id(i['metricOf']['id'])
            print(f"{i[sort_by]} - {uuid} ({', '.join(i['metricOf']['type'])})")
        print("")
        print("Distribution:")
        print(f"0: {len(range_map['0'])}")
        ranges.reverse()
        for r in ranges:
            range_key = f">{r}"
            print(f"{range_key}: {len(range_map[range_key]) if range_key in range_map else 0}")
        print("************")
        print("")
        print("")


def run(properties: dict, kg: KGv3):
    GetViewAndDownloadStats(kg, properties, False).stats()


def simulate(properties: dict, kg: KGv3):
    GetViewAndDownloadStats(kg, properties, True).stats()


if __name__ == '__main__':
    GetViewAndDownloadStats(KGv3("core.kg.ebrains.eu", token_handler=SimpleToken(os.getenv("KG_TOKEN"))), {"filterType": "https://openminds.ebrains.eu/core/DatasetVersion"}, True).stats()
    #GetViewAndDownloadStats(KGv3("core.kg.ebrains.eu", token_handler=SimpleToken(os.getenv("KG_TOKEN"))), {"filterType": None}, True).stats()
