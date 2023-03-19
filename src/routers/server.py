from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks
import requests

from src.internal.type import Resp, WsType, Status
from src.internal.manager import Job
from src.utils.config import manager
from src.utils.ws import update
from src.utils.config import cluster_group
from src.internal.auth import verify_setup


router = APIRouter(tags=["server"])


@router.get("/cloud/server/", dependencies=[Depends(verify_setup)])
async def server_ls(pod_id: str | None = None) -> Resp:
    return Resp(status=False)


@router.post("/cloud/server/launch/", dependencies=[Depends(verify_setup)])
async def server_launch(background_tasks: BackgroundTasks, pod_id: str) -> Resp:
    """cloud server launch POD_ID"""
    try:
        location = manager.get_pod_location(pod_id)
    except Exception as e:
        print(e)
        return Resp(status=False, msg=f"manager: {e}")

    resp = requests.post(
        cluster_group[location.get_cluster_type()][location.get_cluster_id()]
        + "/cloud/server/launch/",
        params={"pod_id": pod_id},
    ).json()
    if resp["status"] == False:
        return Resp(status=False, msg=resp["msg"])

    print(resp["data"])
    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True, msg=resp["msg"])


@router.post("/cloud/server/resume/", dependencies=[Depends(verify_setup)])
async def server_resume(background_tasks: BackgroundTasks, pod_id: str) -> Resp:
    """cloud server resume POD_ID"""
    try:
        location = manager.get_pod_location(pod_id)
    except Exception as e:
        print(e)
        return Resp(status=False, msg=f"manager: {e}")

    resp = requests.post(
        cluster_group[location.get_cluster_type()][location.get_cluster_id()]
        + "/cloud/server/resume/",
        params={"pod_id": pod_id},
    ).json()
    if resp["status"] == False:
        return Resp(status=False, msg=resp["msg"])

    print(resp["data"])
    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True, msg=resp["msg"])


@router.post("/cloud/server/pause/", dependencies=[Depends(verify_setup)])
async def server_pause(background_tasks: BackgroundTasks, pod_id: str) -> Resp:
    """cloud server pause POD_ID"""
    try:
        location = manager.get_pod_location(pod_id)
    except Exception as e:
        print(e)
        return Resp(status=False, msg=f"manager: {e}")

    resp = requests.post(
        cluster_group[location.get_cluster_type()][location.get_cluster_id()]
        + "/cloud/server/pause/",
        params={"pod_id": pod_id},
    ).json()
    if resp["status"] == False:
        return Resp(status=False, msg=resp["msg"])

    print(resp["data"])
    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True, msg=resp["msg"])
