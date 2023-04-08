import httpx
import asyncio

from src.internal.manager import Location
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

        for cluster_type in cluster_group.keys():
            if manager.queue:
                async with httpx.AsyncClient() as client:
                    res = (
                        await client.get(
                            cluster_group[cluster_type]["default"]
                            + "/internal/available"
                        )
                    ).json()

                if res["status"]:
                    job = manager.queue.popleft()
                    job.job_status = Status.RUNNING
                    print("--------------------")
                    with open(f"tmp/{job.job_id}.sh", "rb") as f:
                        async with httpx.AsyncClient() as client:
                            res = (
                                await client.post(
                                    cluster_group[cluster_type]["default"]
                                    + "/cloud/job/",
                                    params={
                                        "job_name": job.job_name,
                                        "job_id": job.job_id,
                                    },
                                    files={"job_script": f},
                                )
                            ).json()
                            print(res)
                            manager.jobs[job.job_id].node_id = res["data"]["node_id"]
                            manager.jobs[job.job_id].pod_id = res["data"]["pod_id"]
                            manager.add_job(
                                job.job_id,
                                Location(
                                    cluster_type=cluster_type, cluster_id="default"
                                ),
                            )

                    print("Job allocated")
                    print(f"Name: {job.job_name}")
                    print(f"ID: {job.job_id}")
                    print(f"NodeID: {job.node_id}")
                    print("--------------------")
                    await update(WsType.JOB)
                    await update(WsType.NODE)
        else:
            print(f"{count}: waiting for jobs")
