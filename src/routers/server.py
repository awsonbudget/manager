import subprocess
from urllib.parse import urlparse

import requests
from fastapi import APIRouter, Depends, BackgroundTasks

from src.internal.type import Resp, WsType
from src.utils.config import manager
from src.utils.ws import update
from src.utils.config import cluster_group, is_prod
from src.internal.auth import verify_setup


router = APIRouter(tags=["server"])


@router.get("/cloud/server/", dependencies=[Depends(verify_setup)])
async def server_ls(
    background_tasks: BackgroundTasks, pod_id: str, node_id: str | None = None
) -> Resp:
    try:
        location = manager.get_pod_location(pod_id)
    except Exception as e:
        print(e)
        return Resp(status=False, msg=f"manager: {e}")

    resp = requests.get(
        cluster_group[location.get_cluster_type()][location.get_cluster_id()]
        + "/cloud/server/",
        params={"pod_id": pod_id, "node_id": node_id},
    ).json()
    if resp["status"] == False:
        return Resp(status=False, msg=resp["msg"])

    print(resp["data"])
    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True, msg=resp["msg"], data=resp["data"])


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

    if is_prod:
        server_type = location.get_cluster_type()
        for server in resp["data"]:
            backend_name = f"{server_type}_pod"
            server_name = server["node_id"]
            ip_addr = urlparse(
                cluster_group[location.get_cluster_type()][location.get_cluster_id()]
            ).netloc.split(":")[0]
            port = server["port"]
            command = f"echo 'experimental-mode on; add server {backend_name}/{server_name} {ip_addr}:{port}' | sudo socat stdio /var/run/haproxy/admin.sock"
            print("HAProxy add: " + command)
            subprocess.run(command, shell=True, check=True)
            command = f"echo 'experimental-mode on; set server {backend_name}/{server_name} state ready' | sudo socat stdio /var/run/haproxy/admin.sock"
            print("HAProxy set: " + command)
            subprocess.run(command, shell=True, check=True)

    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True, msg=resp["msg"], data=resp["data"])


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

    if is_prod:
        server_type = location.get_cluster_type()
        for server in resp["data"]:
            backend_name = f"{server_type}_pod"
            server_name = server["node_id"]
            command = f"echo 'experimental-mode on; set server {backend_name}/{server_name} state ready' | sudo socat stdio /var/run/haproxy/admin.sock"
            print("HAProxy set: " + command)
            subprocess.run(command, shell=True, check=True)

    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True, msg=resp["msg"], data=resp["data"])


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

    if is_prod:
        server_type = location.get_cluster_type()
        for server in resp["data"]:
            backend_name = f"{server_type}_pod"
            server_name = server["node_id"]
            command = f"echo 'experimental-mode on; set server {backend_name}/{server_name} state maint' | sudo socat stdio /var/run/haproxy/admin.sock"
            print("HAProxy set: " + command)
            subprocess.run(command, shell=True, check=True)

    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True, msg=resp["msg"], data=resp["data"])
