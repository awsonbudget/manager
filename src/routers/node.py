from fastapi import APIRouter, Depends
import requests

from src.internal.type import Resp, WsType
from src.internal.manager import clusters, update
from src.internal.auth import verify_setup


router = APIRouter(tags=["node"])


@router.get("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_ls(pod_name: str | None = None) -> Resp:
    """monitoring: 2. cloud node ls [RES_POD_ID]"""
    return Resp.parse_raw(
        requests.get(
            clusters["5551"] + "/cloud/node/", params={"pod_name": pod_name}
        ).content
    )


@router.post("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_register(node_name: str, pod_name: str | None = None) -> Resp:
    """management: 4. cloud register NODE_NAME [POD_ID]"""
    resp = Resp.parse_raw(
        requests.post(
            clusters["5551"] + "/cloud/node/",
            params={"node_name": node_name, "pod_name": pod_name},
        ).content
    )
    await update(WsType.NODE)
    return resp


@router.delete("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_rm(node_name: str) -> Resp:
    """management: 5. cloud rm NODE_NAME"""
    resp = Resp.parse_raw(
        requests.delete(
            clusters["5551"] + "/cloud/node/",
            params={"node_name": node_name},
        ).content
    )
    await update(WsType.NODE)
    return resp


@router.get("/cloud/node/log/", dependencies=[Depends(verify_setup)])
async def node_log(node_id: str) -> Resp:
    """monitoring: 5. cloud node log NODE_ID"""
    return Resp.parse_raw(
        requests.get(
            clusters["5551"] + "/cloud/node/log/",
            params={"node_id": node_id},
        ).content
    )
