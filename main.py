from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from core.database import Base, engine

from routers import (admin_auth, tmsiti_haqida, rahbariyat, tashkil_tuzilma,
                     tarkibiy_bolinma, vakansiya, qonun_qaror_farmon, tizim,
                     shaharsozlik_norma_qoida_bolim, guruh, full_tizim,
                     standart, reglament, smeta_resurs_norma, malumotnoma,
                     management_system_page, elon, yangilik, corrupsiya,
                     tmsiti_boglanish_malumoti, boglanish_form, menu)

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
app.include_router(smeta_resurs_norma.router)
app.include_router(malumotnoma.router)
app.include_router(management_system_page.router)
app.include_router(elon.router)
app.include_router(yangilik.router)
app.include_router(corrupsiya.router)
app.include_router(tmsiti_boglanish_malumoti.router)
app.include_router(boglanish_form.router)
app.include_router(menu.router)
