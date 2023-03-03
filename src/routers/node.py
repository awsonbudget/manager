from fastapi import APIRouter, Depends, BackgroundTasks
import requests

from src.internal.type import Resp, WsType
from src.internal.manager import clusters, update
from src.internal.auth import verify_setup


router = APIRouter(tags=["node"])

## List all the nodes
@router.get("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_ls(pod_id: str | None = None) -> Resp:
    """monitoring: 2. cloud node ls [RES_POD_ID]"""
    return Resp.parse_raw(
        requests.get(
            clusters["5551"] + "/cloud/node/", params={"pod_id": pod_id}
        ).content
    )

## Register node with pod id and node name
@router.post("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_register(
    background_tasks: BackgroundTasks, node_name: str, pod_id: str | None = None
) -> Resp:
    """management: 4. cloud register NODE_NAME [POD_ID]"""
    if len(node_name) >= 16:
        return Resp(status=False, msg="manager: node name is too long!")
    resp = Resp.parse_raw(
        # Send post request to the cluster with pod id and node name
        requests.post(
            clusters["5551"] + "/cloud/node/",
            params={"node_name": node_name, "pod_id": pod_id},
        ).content
    )
    background_tasks.add_task(update, WsType.POD)
    background_tasks.add_task(update, WsType.NODE)
    return resp

## Delete node
@router.delete("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_rm(background_tasks: BackgroundTasks, node_name: str) -> Resp:
    """management: 5. cloud rm NODE_NAME"""
    resp = Resp.parse_raw(
        requests.delete(
        # Send delete request to the cluster with node name
            clusters["5551"] + "/cloud/node/",
            params={"node_name": node_name},
        ).content
    )
    background_tasks.add_task(update, WsType.POD)
    background_tasks.add_task(update, WsType.NODE)
    return resp

## Get node log
@router.get("/cloud/node/log/", dependencies=[Depends(verify_setup)])
async def node_log(node_id: str) -> Resp:
    """monitoring: 5. cloud node log NODE_ID"""
    return Resp.parse_raw(
        # Send get request to the cluster with node name to get the log
        requests.get(
            clusters["5551"] + "/cloud/node/log/",
            params={"node_id": node_id},
        ).content
    )
