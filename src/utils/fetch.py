import requests

from src.internal.type import Resp
from src.utils.config import clusters, manager


async def fetch_pods():
    data = []
    endpoint = "/cloud/pod/"

    for name, addr in clusters.items():
        resp = requests.get(addr + endpoint).json()
        if resp["status"] != True:
            return Resp(
                status=False, msg=f"manager: cluster [{name}] reported an error!"
            )
        data.extend(resp["data"])

    return Resp(status=True, data=data)


async def fetch_nodes(pod_id: str | None):
    endpoint = "/cloud/node/"
    if pod_id != None:
        cluster = manager.pod_map.get(pod_id)
        if cluster is None:
            return Resp(status=False, msg=f"manager: node_id {pod_id} not found")
        resp = requests.get(
            clusters[cluster] + endpoint, params={"pod_id": pod_id}
        ).json()
        if resp["status"] != True:
            return Resp(status=False, msg=resp["msg"])
        return Resp(status=True, data=resp["data"])

    else:
        data = []
        for name, addr in clusters.items():
            resp = requests.get(addr + endpoint).json()
            if resp["status"] != True:
                return Resp(
                    status=False, msg=f"manager: cluster [{name}] reported an error!"
                )
            data.extend(resp["data"])

        return Resp(status=True, data=data)
