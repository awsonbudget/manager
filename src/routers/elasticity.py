import httpx

from fastapi import APIRouter, Depends
from src.internal.type import Resp
from src.utils.config import manager, cluster_group
from src.internal.auth import verify_setup


router = APIRouter(tags=["elasticity"])


@router.post("/cloud/elasticity/lower/", dependencies=[Depends(verify_setup)])
async def set_lower_threshold(pod_id: str, lower_threshold: int):
    try:
        location = manager.get_pod_location(pod_id)
    except Exception as e:
        print(e)
        return Resp(status=False, msg=f"manager: {e}")

    async with httpx.AsyncClient(
        base_url=cluster_group[location.get_cluster_type()][location.get_cluster_id()]
    ) as client:
        resp = (
            await client.get(
                "/cloud/elasticity/lower/",
                params={"lower_threshold": lower_threshold, "pod_id": pod_id},
            )
        ).json()
        if resp["status"] == False:
            return Resp(status=False)
        return Resp(status=True)


@router.post("/cloud/elasticity/upper/", dependencies=[Depends(verify_setup)])
async def set_upper_threshold(pod_id: str, upper_threshold: int):
    try:
        location = manager.get_pod_location(pod_id)
    except Exception as e:
        print(e)
        return Resp(status=False, msg=f"manager: {e}")

    async with httpx.AsyncClient(
        base_url=cluster_group[location.get_cluster_type()][location.get_cluster_id()]
    ) as client:
        resp = (
            await client.get(
                "/cloud/elasticity/upper/",
                params={"upper_threshold": upper_threshold, "pod_id": pod_id},
            )
        ).json()
        if resp["status"] == False:
            return Resp(status=False)
        return Resp(status=True)


@router.post("/cloud/elasticity/enable/", dependencies=[Depends(verify_setup)])
async def enable(pod_id: str, min_node: int, max_node: int):
    try:
        location = manager.get_pod_location(pod_id)
    except Exception as e:
        print(e)
        return Resp(status=False, msg=f"manager: {e}")

    async with httpx.AsyncClient(
        base_url=cluster_group[location.get_cluster_type()][location.get_cluster_id()]
    ) as client:
        resp = (
            await client.get(
                "/cloud/elasticity/enable/",
                params={"pod_id": pod_id, "min_node": min_node, "max_node": max_node},
                timeout=None,
            )
        ).json()
        if resp["status"] == False:
            return Resp(status=False, msg=f"manager: {resp['msg']}")
        return Resp(status=True)


@router.post("/cloud/elasticity/disable/", dependencies=[Depends(verify_setup)])
async def disable(pod_id: str):
    try:
        location = manager.get_pod_location(pod_id)
    except Exception as e:
        print(e)
        return Resp(status=False, msg=f"manager: {e}")

    async with httpx.AsyncClient(
        base_url=cluster_group[location.get_cluster_type()][location.get_cluster_id()]
    ) as client:
        resp = (
            await client.get("/cloud/elasticity/disable/", params={"pod_id": pod_id})
        ).json()
        if resp["status"] == False:
            return Resp(status=False)
        return Resp(status=True)
