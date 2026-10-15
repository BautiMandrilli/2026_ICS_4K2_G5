from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv


load_dotenv(Path(__file__).parent / ".env", override=False)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.interfaces.rutas.compras import router as compras_router
from app.interfaces.rutas.sesiones import router as sesiones_router
from app.infraestructura.base_de_datos.usuarios import inicializar_base_de_datos


@asynccontextmanager
async def lifespan(app: FastAPI):
	inicializar_base_de_datos()
	yield


app = FastAPI(title="EcoHarmony Park", lifespan=lifespan)
app.mount(
	"/static",
	StaticFiles(directory=Path(__file__).parent / "interfaces" / "estaticos"),
	name="static",
)
app.include_router(sesiones_router)
app.include_router(compras_router)
