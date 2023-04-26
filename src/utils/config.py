import json
import pickle

import etcd3

from src.internal.manager import Manager


with open("config.json") as f:
    config = json.load(f)
    is_prod = config["prod"]
    if is_prod:
        etcd_client = etcd3.client(
            host=config["etcd"]["host"], port=config["etcd"]["port"]
        )
        prev_state = etcd_client.get("manager")[0]
        if prev_state:
            print("Previous state found, loading...")
        else:
            print("No previous state found, clean start!")
    manager = pickle.loads(prev_state) if prev_state else Manager()  # type: ignore
    cluster_group = config["cluster_group"]
