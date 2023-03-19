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


class Location(object):
    def __init__(self, cluster_type: str, cluster_id: str):
        self.cluster_type: str = cluster_type
        self.cluster_id: str = cluster_id

    def get_cluster_type(self) -> str:
        return self.cluster_type

    def get_cluster_id(self) -> str:
        return self.cluster_id


class Manager(object):
    def __init__(self):
        self.queue: deque[Job] = deque()
        self.jobs: dict[str, Job] = dict()
        self.__pod_map: dict[str, Location] = dict()  # key is the pod id
        self.__node_map: dict[str, Location] = dict()  # key is the node id
        self.init = False
        self.ws = ConnectionManager()

    def add_pod(self, pod_id: str, location: Location):
        if pod_id in self.__pod_map:
            raise Exception("Pod already exists")
        self.__pod_map[pod_id] = location

    def get_pod_location(self, pod_id: str) -> Location:
        try:
            return self.__pod_map[pod_id]
        except KeyError:
            raise Exception("Pod does not exist")

    def remove_pod(self, pod_id: str):
        try:
            del self.__pod_map[pod_id]
        except KeyError:
            raise Exception("Pod does not exist")

    def add_node(self, node_id: str, location: Location):
        if node_id in self.__node_map:
            raise Exception("Node already exists")
        self.__node_map[node_id] = location

    def get_node_location(self, node_id: str) -> Location:
        try:
            return self.__node_map[node_id]
        except KeyError:
            raise Exception("Node does not exist")

    def remove_node(self, node_id: str):
        try:
            del self.__node_map[node_id]
        except KeyError:
            raise Exception("Node does not exist")


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
