from collections import deque
import uuid

from fastapi import WebSocket

from src.internal.type import Status


class Job(object):
    def __init__(self, name: str, status: Status = Status.REGISTERED):
        # FIXME: Add cluster field
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
        self.pod_map: dict[str, str] = dict()
        self.node_map: dict[str, str] = dict()
        self.init = False
        self.ws = ConnectionManager()


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
