import requests

from src.internal.type import Resp
from src.utils.config import clusters


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


async def fetch_nodes():
    data = []
    endpoint = "/cloud/node/"

    for name, addr in clusters.items():
        resp = requests.get(addr + endpoint).json()
        if resp["status"] != True:
            return Resp(
                status=False, msg=f"manager: cluster [{name}] reported an error!"
            )
        data.extend(resp["data"])

    return Resp(status=True, data=data)
