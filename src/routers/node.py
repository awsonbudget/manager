from fastapi import APIRouter, Depends, BackgroundTasks
import requests

from src.internal.type import Resp, WsType
from src.utils.config import manager
from src.utils.fetch import fetch_nodes
from src.utils.ws import update
from src.internal.auth import verify_setup
from src.utils.config import clusters


router = APIRouter(tags=["node"])


@router.get("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_ls(pod_id: str | None = None) -> Resp:
    """monitoring: 2. cloud node ls [RES_POD_ID]"""
    return await fetch_nodes(pod_id)


@router.post("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_register(
    background_tasks: BackgroundTasks, node_name: str, pod_id: str
) -> Resp:
    """management: 4. cloud register NODE_NAME POD_ID"""
    if len(node_name) >= 16:
        return Resp(status=False, msg="manager: node name is too long!")
    cluster = manager.pod_map.get(pod_id)
    if cluster is None:
        return Resp(status=False, msg=f"manager: pod_id {pod_id} not found")
    resp = requests.post(
        clusters[cluster] + "/cloud/node/",
        params={"node_name": node_name, "pod_id": pod_id},
    ).json()
    if resp["status"] == False:
        return Resp(status=False, msg=resp["msg"])
    manager.node_map[resp["data"]] = cluster  # resp["data"] is node_id
    background_tasks.add_task(update, WsType.POD)
    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True, data=resp["msg"], msg=resp["msg"])


@router.delete("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_rm(background_tasks: BackgroundTasks, node_id: str) -> Resp:
    """management: 5. cloud rm NODE_NAME"""
    cluster = manager.node_map.get(node_id)
    if cluster is None:
        return Resp(status=False, msg=f"manager: node_id {node_id} not found")
    resp = requests.delete(
        clusters[cluster] + "/cloud/node/",
        params={"node_id": node_id},
    ).json()
    if resp["status"] == False:
        return Resp(status=False, msg=resp["msg"])
    manager.node_map.pop(node_id)
    background_tasks.add_task(update, WsType.POD)
    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True, msg=resp["msg"])


@router.get("/cloud/node/log/", dependencies=[Depends(verify_setup)])
async def node_log(node_id: str) -> Resp:
    """monitoring: 5. cloud node log NODE_ID"""
    cluster = manager.node_map.get(node_id)
    if cluster is None:
        return Resp(status=False, msg=f"manager: node_id {node_id} not found")
    return Resp.parse_raw(
        requests.get(
            clusters[cluster] + "/cloud/node/log/",
            params={"node_id": node_id},
        ).content
    )
