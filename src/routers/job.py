import os

from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks
import requests

from src.internal.type import Resp, WsType, Status
from src.internal.manager import Job
from src.utils.config import manager
from src.utils.ws import update
from src.utils.config import cluster_group
from src.internal.auth import verify_setup


router = APIRouter(tags=["job"])


@router.get("/cloud/job/", dependencies=[Depends(verify_setup)])
async def job_ls(node_id: str | None = None) -> Resp:
    """monitoring: 3. cloud job ls [NODE_ID]"""
    if node_id != None:
        return Resp(
            status=True,
            data=[j.toJSON() for j in manager.jobs.values() if j.node == node_id],
        )

    return Resp(status=True, data=[j.toJSON() for j in manager.jobs.values()])


@router.post("/cloud/job/", dependencies=[Depends(verify_setup)])
async def job_launch(job_name: str, job_script: UploadFile) -> Resp:
    """management: 6. cloud launch PATH_TO_JOB"""
    job = Job(name=job_name)
    manager.queue.append(job)
    print(manager.queue)
    manager.jobs[job.id] = job

    os.makedirs("tmp", exist_ok=True)
    with open(os.path.join("tmp", f"{job.id}.sh"), "wb") as f:
        f.write(await job_script.read())

    await update(WsType.JOB)
    return Resp(status=True, data={"job_id": job.id})


@router.delete("/cloud/job/", dependencies=[Depends(verify_setup)])
async def job_abort(background_tasks: BackgroundTasks, job_id: str) -> Resp:
    """cloud abort JOB_ID"""
    try:
        location = manager.get_job_location(job_id)
    except Exception as e:
        return Resp(status=False, msg=f"manager: {e}")

    job = manager.jobs.get(job_id, None)
    if job == None:
        return Resp(status=False, msg="manager: job not found in the job list")

    job.status = Status.ABORTED

    resp = Resp.parse_raw(
        requests.delete(
            cluster_group[location.get_cluster_type()][location.get_cluster_id()]
            + "/cloud/job/",
            params={"job_id": job_id},
        ).content
    )
    background_tasks.add_task(update, WsType.NODE)
    background_tasks.add_task(update, WsType.JOB)
    return resp


@router.get("/cloud/job/log/", dependencies=[Depends(verify_setup)])
async def job_log(job_id: str) -> Resp:
    """cloud job log JOB_ID"""
    try:
        location = manager.get_job_location(job_id)
    except Exception as e:
        return Resp(status=False, msg=f"manager: {e}")
    return Resp.parse_raw(
        requests.get(
            cluster_group[location.get_cluster_type()][location.get_cluster_id()]
            + "/cloud/job/log/",
            params={"job_id": job_id},
        ).content
    )
