from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
# from auth.auth import auth_backend
import uvicorn

# from auth.database import User
# from auth.manager import get_user_manager

# from auth.schemas import UserCreate, UserRead

import os

from db.base import metadata
from db.database import engine

from api.router import router as api_router
from api.auth.router import router as auth_router
from api.post.router import router as post_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    
    #
    await create_tables()
    
    yield

    # await drop_tables()

    # 


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

async def drop_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


app = FastAPI(lifespan=lifespan)



app.include_router(router=api_router)
app.include_router(router=auth_router, tags=["auth"])
app.include_router(router=post_router,prefix="/post" , tags=["post"])


