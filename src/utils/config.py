import os
import json

from src.internal.manager import Manager

manager = Manager()

config_file = "prod-config.json" if os.environ.get("PROD") else "dev-config.json"
print(f"Using config file: {config_file}")

with open(config_file) as f:
    cluster_group = json.load(f)["cluster_group"]
