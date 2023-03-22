import requests
import asyncio
from src.internal.type import Status, WsType
from src.utils.config import manager, cluster_group
from src.utils.ws import update


async def main_worker():
    # FIXME: Fix worker to support non-default pods
    count = 0
    while True:
        print(manager.queue)
        await asyncio.sleep(3)
        count += 1
        if manager.queue:
            for cluster_type in cluster_group.keys():
                res = requests.get(
                    cluster_group[cluster_type]["default"] + "/internal/available"
                ).json()
                if res["status"]:
                    job = manager.queue.popleft()
                    job.status = Status.RUNNING
                    print("--------------------")
                    with open(f"tmp/{job.id}.sh") as f:
                        res = requests.post(
                            cluster_group[cluster_type]["default"] + "/cloud/job/",
                            params={
                                "job_name": job.name,
                                "job_id": job.id,
                            },
                            files={"job_script": f},
                        ).json()
                        print(res)
                        manager.jobs[job.id].node = res["data"]["node_id"]

                    print("Job allocated")
                    print(f"Name: {job.name}")
                    print(f"ID: {job.id}")
                    print(f"Node: {job.node}")
                    print("--------------------")
                    await update(WsType.JOB)
                    await update(WsType.NODE)
        else:
            print(f"{count}: waiting for jobs")
