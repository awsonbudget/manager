from __future__ import annotations
from enum import Enum

from pydantic import BaseModel


class Resp(BaseModel):
    status: bool
    msg: str = ""
    data: list | dict | str | None = None


class WsResp(BaseModel):
    type: WsType
    data: list


class WsType(str, Enum):
    POD = "pod"
    NODE = "node"
    JOB = "job"
    ERROR = "error"


class Status(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    REGISTERED = "registered"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"
