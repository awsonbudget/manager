import shutil
import subprocess

from fastapi import APIRouter
import requests

from src.internal.manager import Location
from src.internal.type import Resp, WsType
from src.utils.config import manager, cluster_group, is_prod
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

    if is_prod:
        subprocess.run("sudo systemctl haproxy restart", shell=True)

    # TODO: Make this concurrent
    for type, clusters in cluster_group.items():
        for cluster_id, addr in clusters.items():
            res = requests.post(addr + "/cloud/", params={"type": type}).json()
            if res["status"] == False:
                return Resp(
                    status=False,
                    msg=f"manager: {type} cluster {cluster_id} failed to initialize",
                )
            res = requests.post(
                addr + "/cloud/pod/", params={"pod_name": f"{type}-{cluster_id}"}
            ).json()
            if res["status"] == False:
                return Resp(
                    status=False,
                    msg=f"manager: {type} cluster {cluster_id} failed to create pod",
                )
            manager.add_pod(
                res["data"], Location(type, cluster_id)
            )  # res.data here is the pod_id

    manager.init = True
    await update(WsType.POD)
    await update(WsType.NODE)
    await update(WsType.JOB)
    return Resp(status=True, msg="manager: all cluster initialized")
