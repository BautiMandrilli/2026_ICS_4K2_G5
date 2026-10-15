from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.interfaces.rutas.compras import router as compras_router


app = FastAPI(title="EcoHarmony Park")
app.mount(
	"/static",
	StaticFiles(directory=Path(__file__).parent / "interfaces" / "estaticos"),
	name="static",
)
app.include_router(compras_router)
