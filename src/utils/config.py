import json

from src.internal.manager import Manager

manager = Manager()

with open("config.json") as f:
    config = json.load(f)
    cluster_group = config["cluster_group"]
    is_prod = config["prod"]
