import json
from src.internal.manager import Manager

manager = Manager()

with open("config.json") as f:
    cluster_group = json.load(f)["cluster_group"]
