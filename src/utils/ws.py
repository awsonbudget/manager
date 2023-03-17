import json

from src.internal.type import WsType
from src.utils.config import manager
from src.utils.fetch import fetch_pods, fetch_nodes


async def update(type: WsType):
    print("There are", len(manager.ws.active_connections), "active WS connection(s)")
    match type:
        case WsType.POD:
            await manager.ws.broadcast(
                json.dumps({"type": WsType.POD, "data": (await fetch_pods()).data})
            )
        case WsType.NODE:
            await manager.ws.broadcast(
                json.dumps(
                    {"type": WsType.NODE, "data": (await fetch_nodes(None)).data}
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
