import requests

from src.internal.type import Resp
from src.utils.config import cluster_group, manager


async def fetch_pods():
    data = []
    endpoint = "/cloud/pod/"

    for type, clusters in cluster_group.items():
        for cluster_id, addr in clusters.items():
            resp = requests.get(addr + endpoint).json()
            if resp["status"] != True:
                return Resp(
                    status=False,
                    msg=f"manager: {type} cluster [{cluster_id}] reported an error!",
                )
            data.extend(resp["data"])

    return Resp(status=True, data=data)


async def fetch_nodes(pod_id: str | None):
    endpoint = "/cloud/node/"
    if pod_id != None:
        try:
            location = manager.get_pod_location(pod_id)
        except Exception as e:
            print(e)
            return Resp(status=False, msg=f"manager: {e}")

        resp = requests.get(
            cluster_group[location.get_cluster_type()][location.get_cluster_id()]
            + endpoint,
            params={"pod_id": pod_id},
        ).json()

        if resp["status"] != True:
            return Resp(status=False, msg=resp["msg"])
        return Resp(status=True, data=resp["data"])

    else:
        data = []
        for type, clusters in cluster_group.items():
            for cluster_id, addr in clusters.items():
                resp = requests.get(addr + endpoint).json()
                if resp["status"] != True:
                    return Resp(
                        status=False,
                        msg=f"manager: {type} cluster [{cluster_id}] reported an error!",
                    )
                data.extend(resp["data"])

        return Resp(status=True, data=data)