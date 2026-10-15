from pathlib import Path
from datetime import date

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.aplicacion.casos_de_uso.comprar_entradas import comprar_entradas


router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "plantillas")


@router.get("/", response_class=HTMLResponse)
def mostrar_compra(request: Request):
	return templates.TemplateResponse(
		request=request,
		name="compra.html",
		context={},
	)


@router.post("/compras", response_class=HTMLResponse)
def procesar_compra(
	request: Request,
	fecha_visita: date = Form(...),
	cantidad: int = Form(...),
	edades: list[int] = Form(...),
	tipo_de_pase: str = Form(...),
	forma_de_pago: str = Form(...),
):
	try:
		if forma_de_pago != "efectivo":
			raise ValueError("El pago con tarjeta se implementara en la siguiente etapa")
		resultado = comprar_entradas(
			usuario="visitante_demo",
			fecha_visita=fecha_visita,
			cantidad=cantidad,
			edades=edades,
			tipo_de_pase=tipo_de_pase,
			forma_de_pago=forma_de_pago,
		)
		errors = None
	except (PermissionError, ValueError) as error:
		resultado = None
		errors = str(error)

	return templates.TemplateResponse(
		request=request,
		name="compra.html",
		context={"error": errors, "resultado": resultado},
		status_code=400 if errors else 200,
	)
