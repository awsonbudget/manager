from fastapi import APIRouter, Depends, BackgroundTasks
import requests

from src.internal.type import Resp, WsType
from src.internal.manager import clusters, update
from src.internal.auth import verify_setup


router = APIRouter(tags=["pod"])

## List all the pods
@router.get("/cloud/pod/", dependencies=[Depends(verify_setup)])
async def pod_ls() -> Resp:
    """monitoring: 1. cloud pod ls"""
    # Send get request to the cluster 
    return Resp.parse_raw(requests.get(clusters["5551"] + "/cloud/pod/").content)

## Register pod with pod name
@router.post("/cloud/pod/", dependencies=[Depends(verify_setup)])
async def pod_register(background_tasks: BackgroundTasks, pod_name: str) -> Resp:
    """management: 2. cloud pod register POD_NAME"""
    if len(pod_name) >= 16:
        return Resp(status=False, msg="manager: pod name is too long!")
    resp = Resp.parse_raw(
        # Send post request to the cluster with pod name given
        requests.post(
            clusters["5551"] + "/cloud/pod/", params={"pod_name": pod_name}
        ).content
    )
    background_tasks.add_task(update, WsType.POD)
    return resp

## Delete pod
@router.delete("/cloud/pod/", dependencies=[Depends(verify_setup)])
async def pod_rm(background_tasks: BackgroundTasks, pod_name: str):
    "management: 3. cloud pod rm POD_NAME"
    resp = Resp.parse_raw(
        # Send delete request to the cluster with pod name given
        requests.delete(
            clusters["5551"] + "/cloud/pod/", params={"pod_name": pod_name}
        ).content
    )
    background_tasks.add_task(update, WsType.POD)
    return resp
