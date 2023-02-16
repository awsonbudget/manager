from __future__ import annotations
from enum import Enum
import requests
import time
from collections import deque
from fastapi import FastAPI, UploadFile, Request, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uuid
import asyncio
import os
import shutil
from dotenv import dotenv_values

app = FastAPI()
config = dotenv_values(".env")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(manager.main_worker())


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


async def verify_setup():
    if manager.init == False:
        raise HTTPException(status_code=400, detail="cluster: please initialize first")


class Resp(BaseModel):
    status: bool
    msg: str = ""
    data: list | dict | str | None = None


class Status(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    REGISTERED = "registered"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"


class Job(object):
    def __init__(self, name: str, status: Status = Status.REGISTERED):
        # TODO: manager needs a more centralized view of all jobs
        self.name: str = name
        self.id: str = str(uuid.uuid4())
        self.status: Status = status
        self.node: str | None = None

    def toJSON(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "node": self.node,
        }


class Manager(object):
    def __init__(self):
        self.queue: deque[Job] = deque()
        self.jobs: dict[str, Job] = dict()
        self.init = False
        # self.worker: Process | None = None

    async def main_worker(self):
        count = 0
        while True:
            print(self.queue)
            await asyncio.sleep(3)
            count += 1
            if self.queue:
                res = requests.get(clusters["5551"] + "/internal/available/").json()
                if res["status"]:
                    job = self.queue.pop()
                    job.status = Status.RUNNING
                    print("--------------------")
                    with open(f"tmp/{job.id}.sh") as f:
                        res = requests.post(
                            clusters["5551"] + "/cloud/job/",
                            params={
                                "job_name": job.name,
                                "job_id": job.id,
                            },
                            files={"job_script": f},
                        ).json()
                        self.jobs[job.id].node = res["data"]["node_id"]

                    print("Job allocated")
                    print(f"Name: {job.name}")
                    print(f"ID: {job.id}")
                    print(f"Node: {job.node}")
                    print("--------------------")
            else:
                print(f"{count}: waiting for jobs")


manager = Manager()
assert config["CLUSTER"] != None

clusters: dict[str, str] = {"5551": config["CLUSTER"]}


@app.post("/cloud/")
async def init() -> Resp:
    """management: 1. cloud init"""
    if manager.init == True:
        return Resp(status=True, msg="manager: warning already initialized")

    try:
        shutil.rmtree("tmp")
    except OSError:
        print("tmp was already cleaned")

    for name, url in clusters.items():
        res = requests.post(url + "/cloud/").json()
        if res["status"] == False:
            return Resp(
                status=False, msg=f"manager: cluster {name} failed to initialize"
            )
    manager.init = True
    return Resp(status=True, msg="manager: all cluster initialized")


@app.get("/cloud/pod/", dependencies=[Depends(verify_setup)])
async def pod_ls() -> Resp:
    """monitoring: 1. cloud pod ls"""
    return Resp.parse_raw(requests.get(clusters["5551"] + "/cloud/pod/").content)


@app.post("/cloud/pod/", dependencies=[Depends(verify_setup)])
async def pod_register(pod_name: str) -> Resp:
    """management: 2. cloud pod register POD_NAME"""
    return Resp.parse_raw(
        requests.post(
            clusters["5551"] + "/cloud/pod/", params={"pod_name": pod_name}
        ).content
    )


@app.delete("/cloud/pod/", dependencies=[Depends(verify_setup)])
async def pod_rm(pod_name: str):
    "management: 3. cloud pod rm POD_NAME"
    return Resp.parse_raw(
        requests.delete(
            clusters["5551"] + "/cloud/pod/", params={"pod_name": pod_name}
        ).content
    )


@app.get("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_ls(pod_name: str | None = None) -> Resp:
    """monitoring: 2. cloud node ls [RES_POD_ID]"""
    return Resp.parse_raw(
        requests.get(
            clusters["5551"] + "/cloud/node/", params={"pod_name": pod_name}
        ).content
    )


@app.post("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_register(node_name: str, pod_name: str | None = None) -> Resp:
    """management: 4. cloud register NODE_NAME [POD_ID]"""
    return Resp.parse_raw(
        requests.post(
            clusters["5551"] + "/cloud/node/",
            params={"node_name": node_name, "pod_name": pod_name},
        ).content
    )


@app.delete("/cloud/node/", dependencies=[Depends(verify_setup)])
async def node_rm(node_name: str) -> Resp:
    """management: 5. cloud rm NODE_NAME"""
    return Resp.parse_raw(
        requests.delete(
            clusters["5551"] + "/cloud/node/",
            params={"node_name": node_name},
        ).content
    )


@app.get("/cloud/job/", dependencies=[Depends(verify_setup)])
async def job_ls(node_id: str | None = None) -> Resp:
    """monitoring: 3. cloud job ls [NODE_ID]"""
    if node_id != None:
        return Resp(
            status=True,
            data=[j.toJSON() for j in manager.jobs.values() if j.node == node_id],
        )

    return Resp(status=True, data=[j.toJSON() for j in manager.jobs.values()])


@app.post("/cloud/job/", dependencies=[Depends(verify_setup)])
async def job_launch(job_name: str, job_script: UploadFile) -> Resp:
    """management: 6. cloud launch PATH_TO_JOB"""
    job = Job(name=job_name)
    manager.queue.append(job)
    print(manager.queue)
    manager.jobs[job.id] = job

    os.makedirs("tmp", exist_ok=True)
    with open(os.path.join("tmp", f"{job.id}.sh"), "wb") as f:
        f.write(await job_script.read())

    return Resp(status=True, data={"job_id": job.id})


@app.delete("/cloud/job/", dependencies=[Depends(verify_setup)])
async def job_abort(job_id: str) -> Resp:
    """management: 7. cloud abort JOB_ID"""
    job = manager.jobs.get(job_id, None)
    if job == None:
        return Resp(status=False, msg="manager: job not found in the job list")

    job.status = Status.ABORTED

    return Resp.parse_raw(
        requests.delete(
            clusters["5551"] + "/cloud/job/",
            params={"job_id": job_id},
        ).content
    )


@app.get("/cloud/job/log/", dependencies=[Depends(verify_setup)])
async def job_log(job_id: str) -> Resp:
    """monitoring: 4. cloud job log JOB_ID"""
    return Resp.parse_raw(
        requests.get(
            clusters["5551"] + "/cloud/job/log/",
            params={"job_id": job_id},
        ).content
    )


@app.get("/cloud/node/log/", dependencies=[Depends(verify_setup)])
async def node_log(node_id: str) -> Resp:
    """monitoring: 5. cloud node log NODE_ID"""
    return Resp.parse_raw(
        requests.get(
            clusters["5551"] + "/cloud/node/log/",
            params={"node_id": node_id},
        ).content
    )


@app.post("/internal/callback/", dependencies=[Depends(verify_setup)])
async def callback(job_id: str) -> Resp:
    if job_id not in manager.jobs:
        raise Exception(
            f"manager: job {job_id} received from callback is not in the job list"
        )
    manager.jobs[job_id].status = Status.COMPLETED
    print(f"Job: {job_id} has been completed")
    print(manager.jobs)
    return Resp(status=True)
