import os

from fastapi import APIRouter, Depends, UploadFile
import requests

from src.internal.type import Resp, WsType, Status
from src.internal.manager import clusters, manager, update, Job
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
async def job_abort(job_id: str) -> Resp:
    """management: 7. cloud abort JOB_ID"""
    job = manager.jobs.get(job_id, None)
    if job == None:
        return Resp(status=False, msg="manager: job not found in the job list")

    job.status = Status.ABORTED

    resp = Resp.parse_raw(
        requests.delete(
            clusters["5551"] + "/cloud/job/",
            params={"job_id": job_id},
        ).content
    )
    await update(WsType.JOB)
    return resp


@router.get("/cloud/job/log/", dependencies=[Depends(verify_setup)])
async def job_log(job_id: str) -> Resp:
    """monitoring: 4. cloud job log JOB_ID"""
    return Resp.parse_raw(
        requests.get(
            clusters["5551"] + "/cloud/job/log/",
            params={"job_id": job_id},
        ).content
    )
