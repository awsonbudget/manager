import asyncio
from collections import deque
import json
import uuid

from fastapi import WebSocket
from dotenv import dotenv_values
import requests

from src.internal.type import Status, WsType

## Create job data structure
class Job(object):
    def __init__(self, name: str, status: Status = Status.REGISTERED):
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

## Create Manager data structure
class Manager(object):
    def __init__(self):
        self.queue: deque[Job] = deque()
        self.jobs: dict[str, Job] = dict()
        self.init = False
        self.ws = ConnectionManager()
    # Managing the job queuing process
    async def main_worker(self):
        count = 0
        while True:
            print(self.queue)
            await asyncio.sleep(3)
            count += 1
            if self.queue:
                res = requests.get(clusters["5551"] + "/internal/available").json()
                if res["status"]:
                    # Allocate a job to run
                    job = self.queue.popleft()
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
                    await update(WsType.JOB)
                    await update(WsType.NODE)
            else:
                print(f"{count}: waiting for jobs")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except RuntimeError:
                self.disconnect(connection)

# Manage dataflow update
async def update(type: WsType):
    print(len(manager.ws.active_connections))
    match type:
        case WsType.POD:
            await manager.ws.broadcast(
                json.dumps(
                    {
                        "type": WsType.POD,
                        "data": requests.get(clusters["5551"] + "/cloud/pod/").json()[
                            "data"
                        ],
                    }
                )
            )
        case WsType.NODE:
            await manager.ws.broadcast(
                json.dumps(
                    {
                        "type": WsType.NODE,
                        "data": requests.get(clusters["5551"] + "/cloud/node/").json()[
                            "data"
                        ],
                    }
                )
            )
        case WsType.JOB:
            await manager.ws.broadcast(
                json.dumps(
                    {
                        "type": WsType.JOB,
                        "data": [j.toJSON() for j in manager.jobs.values()],
                    }
                )
            )
        case WsType.ERROR:
            await manager.ws.broadcast(
                json.dumps(
                    {
                        "type": WsType.ERROR,
                    }
                )
            )


config = dotenv_values(".env")
manager = Manager()

assert config["CLUSTER"] != None

clusters: dict[str, str] = {"5551": config["CLUSTER"]}
