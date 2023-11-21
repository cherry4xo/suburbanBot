import json

def get_russia():
    with open("./app/data/data.json", "r") as rf:
        data = (json.load(rf))["countries"]
        with open("data_russia.json", "w", encoding="utf-8") as wf:
            for i in data:
                if "Россия" in i["title"]:
                    json.dump(i, wf, ensure_ascii=False)

def get_only_trains():
    with open("./app/data/data_russia.json") as rf:
        data = (json.load(rf))["regions"]
        res = {}
        with open("./app/data/data_russia_trains.json", "w") as wf:
            for region in data:
                res.update({region["title"]: []})
                for settlement in region["settlements"]:
                    for stations in settlement["stations"]:
                        if stations["transport_type"] == "train":
                            res[region["title"]].append(stations["title"])
            json.dump(res, wf, ensure_ascii=False)

get_only_trains()