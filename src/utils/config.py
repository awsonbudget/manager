from dotenv import dotenv_values

config = dotenv_values(".env")
assert config["CLUSTER_HEAVY"] != None
assert config["CLUSTER_MEDIUM"] != None
assert config["CLUSTER_LIGHT"] != None

clusters: dict[str, str] = {
    "heavy": config["CLUSTER_HEAVY"],
    "medium": config["CLUSTER_MEDIUM"],
    "light": config["CLUSTER_LIGHT"],
}
