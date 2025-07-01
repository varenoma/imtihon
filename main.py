from fastapi import FastAPI
from models import admin
from core.database import Base, engine
import asyncio

from routers import admin_auth

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(admin_auth.router)
