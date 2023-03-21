import subprocess

import requests
from fastapi import APIRouter, Depends, BackgroundTasks

from src.internal.type import Resp, WsType
from src.utils.config import manager
from src.utils.fetch import fetch_nodes
from src.utils.ws import update
from src.internal.auth import verify_setup
from src.utils.config import cluster_group


router = APIRouter(tags=["node"])


@router.get("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_ls(pod_id: str | None = None) -> Resp:
    """monitoring: 2. cloud node ls [RES_POD_ID]"""
    return await fetch_nodes(pod_id)


@router.post("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_register(
    background_tasks: BackgroundTasks, node_type: str, node_name: str, pod_id: str
) -> Resp:
    """management: 4. cloud register NODE_NAME POD_ID"""
    if len(node_name) >= 16:
        return Resp(status=False, msg="manager: node name is too long!")
    try:
        location = manager.get_pod_location(pod_id)
    except Exception as e:
        print(e)
        return Resp(status=False, msg=f"manager: {e}")

    resp = requests.post(
        cluster_group[location.get_cluster_type()][location.get_cluster_id()]
        + "/cloud/node/",
        params={"node_type": node_type, "node_name": node_name, "pod_id": pod_id},
    ).json()
    if resp["status"] == False:
        return Resp(status=False, msg=resp["msg"])

    manager.add_node(resp["data"], location)  # resp["data"] is node_id
    background_tasks.add_task(update, WsType.POD)
    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True, data=resp["msg"], msg=resp["msg"])


@router.delete("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_rm(background_tasks: BackgroundTasks, node_id: str) -> Resp:
    """management: 5. cloud rm NODE_NAME"""
    try:
        location = manager.get_node_location(node_id)
    except Exception as e:
        print(e)
        return Resp(status=False, msg=f"manager: {e}")

    resp = requests.delete(
        cluster_group[location.get_cluster_type()][location.get_cluster_id()]
        + "/cloud/node/",
        params={"node_id": node_id},
    ).json()
    if resp["status"] == False:
        return Resp(status=False, msg=resp["msg"])

    try:
        manager.remove_node(node_id)
    except Exception as e:
        print(e)
        return Resp(status=False, msg=f"manager: {e}")

    if resp["data"]["delete"] == True:
        backend_name = f"{location.get_cluster_type()}_pod"
        server_name = node_id
        command = f"echo 'experimental-mode on; set server {backend_name}/{server_name}' state maint | sudo socat stdio /var/run/haproxy/admin.sock"
        print("HAProxy set: " + command)
        subprocess.run(command, shell=True, check=True)
        command = f"echo 'experimental-mode on; del server {backend_name}/{server_name}' | sudo socat stdio /var/run/haproxy/admin.sock"
        print("HAProxy delete: " + command)
        subprocess.run(command, shell=True, check=True)

    background_tasks.add_task(update, WsType.POD)
    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True, msg=resp["msg"])


@router.get("/cloud/node/log/", dependencies=[Depends(verify_setup)])
async def node_log(node_id: str) -> Resp:
    """cloud node log NODE_ID"""
    try:
        location = manager.get_node_location(node_id)
    except Exception as e:
        print(e)
        return Resp(status=False, msg=f"manager: {e}")

    return Resp.parse_raw(
        requests.get(
            cluster_group[location.get_cluster_type()][location.get_cluster_id()]
            + "/cloud/node/log/",
            params={"node_id": node_id},
        ).content
    )
