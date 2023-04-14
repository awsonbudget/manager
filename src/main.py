import asyncio
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.internal.worker import main_worker, state_saver
from src.routers import init, pod, job, node, server, internal, elasticity

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping/")
async def hello() -> str:
    return "pong"


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main_worker())
    asyncio.create_task(state_saver())


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(init.router)
app.include_router(pod.router)
app.include_router(node.router)
app.include_router(job.router)
app.include_router(server.router)
app.include_router(elasticity.router)
app.include_router(internal.router)
