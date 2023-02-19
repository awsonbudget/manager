from fastapi import HTTPException

from src.internal.manager import manager


async def verify_setup():
    if manager.init == False:
        raise HTTPException(status_code=400, detail="cluster: please initialize first")
