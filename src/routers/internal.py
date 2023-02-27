from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks

from src.internal.type import Resp, WsType, Status
from src.internal.manager import manager, update
from src.internal.auth import verify_setup

router = APIRouter(tags=["internal"])


async def trigger_update():
    await update(WsType.POD)
    await update(WsType.NODE)
    await update(WsType.JOB)


@router.post("/internal/callback/", dependencies=[Depends(verify_setup)])
async def callback(job_id: str, background_tasks: BackgroundTasks) -> Resp:
    if job_id not in manager.jobs:
        raise Exception(
            f"manager: job {job_id} received from callback is not in the job list"
        )
    manager.jobs[job_id].status = Status.COMPLETED
    print(f"Job: {job_id} has been completed")
    print(manager.jobs)
    background_tasks.add_task(trigger_update)
    return Resp(status=True)


@router.websocket("/internal/update/")
async def ws(websocket: WebSocket):
    await manager.ws.connect(websocket)
    try:
        if manager.init:
            await update(WsType.POD)
            await update(WsType.NODE)
            await update(WsType.JOB)
        else:
            await update(WsType.ERROR)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.ws.disconnect(websocket)
