from fastapi import APIRouter, Depends, BackgroundTasks
import requests

from src.internal.type import Resp, WsType
from src.utils.ws import update
from src.internal.auth import verify_setup
from src.utils.fetch import fetch_pods
from src.utils.config import cluster_group


router = APIRouter(tags=["pod"])


@router.get("/cloud/pod/", dependencies=[Depends(verify_setup)])
async def pod_ls() -> Resp:
    """monitoring: 1. cloud pod ls"""
    return await fetch_pods()


@router.post("/cloud/pod/", dependencies=[Depends(verify_setup)])
async def pod_register(background_tasks: BackgroundTasks, pod_name: str) -> Resp:
    """management: 2. cloud pod register POD_NAME"""
    # TODO: Default to light cluster for the moment, make this more flexible in the future
    if len(pod_name) >= 16:
        return Resp(status=False, msg="manager: pod name is too long!")
    resp = Resp.parse_raw(
        requests.post(
            cluster_group["light"]["default"] + "/cloud/pod/",
            params={"pod_name": pod_name},
        ).content
    )
    background_tasks.add_task(update, WsType.POD)
    return resp


@router.delete("/cloud/pod/", dependencies=[Depends(verify_setup)])
async def pod_rm(background_tasks: BackgroundTasks, pod_name: str):
    "management: 3. cloud pod rm POD_NAME"
    # TODO: Default to light cluster for the moment, make this more flexible in the future
    resp = Resp.parse_raw(
        requests.delete(
            cluster_group["light"]["default"] + "/cloud/pod/",
            params={"pod_name": pod_name},
        ).content
    )
    background_tasks.add_task(update, WsType.POD)
    return resp
