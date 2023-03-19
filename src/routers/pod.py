from fastapi import APIRouter, Depends, BackgroundTasks
import requests
from src.internal.manager import Location

from src.internal.type import Resp, WsType
from src.utils.ws import update
from src.internal.auth import verify_setup
from src.utils.fetch import fetch_pods
from src.utils.config import cluster_group, manager


router = APIRouter(tags=["pod"])


@router.get("/cloud/pod/", dependencies=[Depends(verify_setup)])
async def pod_ls() -> Resp:
    """monitoring: 1. cloud pod ls"""
    return await fetch_pods()


@router.post("/cloud/pod/", dependencies=[Depends(verify_setup)])
async def pod_register(
    background_tasks: BackgroundTasks, pod_type: str, pod_name: str
) -> Resp:
    """cloud pod register POD_TYPE POD_NAME"""
    # TODO: Default to the default server for the moment, make this more flexible in the future
    if pod_type not in cluster_group.keys():
        return Resp(status=False, msg="manager: pod type is invalid!")

    if len(pod_name) >= 16:
        return Resp(status=False, msg="manager: pod name is too long!")
    resp = requests.post(
        cluster_group[pod_type]["default"] + "/cloud/pod/",
        params={"pod_name": pod_name},
    ).json()

    if resp["status"] == False:
        return Resp(status=False, msg=resp["msg"])

    manager.add_pod(resp["data"], Location(pod_type, "default"))
    background_tasks.add_task(update, WsType.POD)
    return Resp(status=True, data=resp["data"], msg=resp["msg"])


@router.delete("/cloud/pod/", dependencies=[Depends(verify_setup)])
async def pod_rm(background_tasks: BackgroundTasks, pod_id: str) -> Resp:
    "cloud pod rm POD_ID"
    # TODO: Default to the default server for the moment, make this more flexible in the future
    try:
        location = manager.get_pod_location(pod_id)
    except Exception as e:
        return Resp(status=False, msg=f"{e}")

    resp = Resp.parse_raw(
        requests.delete(
            cluster_group[location.get_cluster_type()][location.get_cluster_id()]
            + "/cloud/pod/",
            params={"pod_id": pod_id},
        ).content
    )
    background_tasks.add_task(update, WsType.POD)
    return resp
