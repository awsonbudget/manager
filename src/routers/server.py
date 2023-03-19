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
    return Resp(status=True)


@router.post("/cloud/server/launch/", dependencies=[Depends(verify_setup)])
async def server_launch(background_tasks: BackgroundTasks, pod_id: str) -> Resp:
    """cloud server launch POD_ID"""
    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True)


@router.post("/cloud/server/resume/", dependencies=[Depends(verify_setup)])
async def server_resume(background_tasks: BackgroundTasks, pod_id: str) -> Resp:
    """cloud server resume POD_ID"""

    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True)


@router.post("/cloud/server/pause/", dependencies=[Depends(verify_setup)])
async def server_pause(background_tasks: BackgroundTasks, pod_id: str) -> Resp:
    """cloud server pause POD_ID"""

    background_tasks.add_task(update, WsType.NODE)
    return Resp(status=True)
