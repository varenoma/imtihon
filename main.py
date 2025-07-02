from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from core.database import Base, engine

from routers import admin_auth, tmsiti_haqida, rahbariyat

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(admin_auth.router)
app.include_router(tmsiti_haqida.router)
app.include_router(rahbariyat.router)
