import shutil

from fastapi import APIRouter
import requests

from src.internal.type import Resp, WsType
from src.utils.config import manager, clusters
from src.utils.ws import update


router = APIRouter(tags=["init"])


@router.post("/cloud/")
async def init() -> Resp:
    """management: 1. cloud init"""
    if manager.init == True:
        return Resp(status=True, msg="manager: warning already initialized")

    try:
        shutil.rmtree("tmp")
    except OSError:
        print("tmp was already cleaned")

    # TODO: Make this concurrent
    for name, url in clusters.items():
        res = requests.post(url + "/cloud/").json()
        if res["status"] == False:
            return Resp(
                status=False, msg=f"manager: cluster {name} failed to initialize"
            )
        res = requests.post(url + "/cloud/pod", params={"pod_name": name}).json()
        if res["status"] == False:
            return Resp(
                status=False, msg=f"manager: cluster {name} failed to create pod"
            )
        manager.pod_map[res["data"]] = name  # res.data here is the pod_id

    manager.init = True
    await update(WsType.POD)
    await update(WsType.NODE)
    await update(WsType.JOB)
    return Resp(status=True, msg="manager: all cluster initialized")
