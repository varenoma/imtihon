from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from core.database import Base, engine

from routers import (admin_auth, tmsiti_haqida, rahbariyat, tashkil_tuzilma,
                     tarkibiy_bolinma, vakansiya, qonun_qaror_farmon, tizim,
                     shaharsozlik_norma_qoida_bolim, guruh, full_tizim,
                     standart, reglament)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(admin_auth.router)
app.include_router(tmsiti_haqida.router)
app.include_router(rahbariyat.router)
app.include_router(tashkil_tuzilma.router)
app.include_router(tarkibiy_bolinma.router)
app.include_router(vakansiya.router)
app.include_router(qonun_qaror_farmon.router)
app.include_router(full_tizim.router)
app.include_router(tizim.router)
app.include_router(shaharsozlik_norma_qoida_bolim.router)
app.include_router(guruh.router)
app.include_router(standart.router)
app.include_router(reglament.router)
