from fastapi import HTTPException

from src.utils.config import manager


async def verify_setup():
    if manager.init == False:
        raise HTTPException(status_code=400, detail="cluster: please initialize first")
