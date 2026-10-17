from __future__ import annotations

from pathlib import Path
from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from pydantic import EmailStr
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.aplicacion.casos_de_uso.comprar_entradas import comprar_entradas
from app.aplicacion.notificaciones import ErrorNotificacion, NotificadorCompra
from app.infraestructura.autenticacion import usuario_actual, usuario_actual_opcional
from app.infraestructura.notificaciones.correo import obtener_notificador
from app.infraestructura.base_de_datos.compras import RepositorioComprasEnMemoria

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "plantillas")
_repositorio_compras = RepositorioComprasEnMemoria()


def repositorio_compras() -> RepositorioComprasEnMemoria:
	return _repositorio_compras

def notificador_compra() -> NotificadorCompra | None:
	try:
		return obtener_notificador()
	except ErrorNotificacion:
		return None


@router.get("/", response_class=HTMLResponse)
def mostrar_compra(request: Request, usuario: dict | None = Depends(usuario_actual_opcional)):
	if usuario is None:
		return RedirectResponse("/login", status_code=303)
	return templates.TemplateResponse(
		request=request,
		name="compra.html",
		context={"usuario": usuario},
	)


@router.post("/compras", response_class=HTMLResponse)
def procesar_compra(
	request: Request,
	fecha_visita: date = Form(...),
	cantidad: int = Form(...),
	edades: list[int] = Form(...),
	tipo_de_pase: str = Form(...),
	forma_de_pago: str = Form(...),
	email: EmailStr = Form(...),
	notificador: NotificadorCompra | None = Depends(notificador_compra),
	usuario: dict = Depends(usuario_actual),
):
	try:
		if forma_de_pago == "tarjeta":
			raise ValueError("El pago con tarjeta se implementara en la siguiente etapa")
		if forma_de_pago not in {"efectivo", "mercadopago"}:
			raise ValueError("La forma de pago no es valida")
		resultado = comprar_entradas(
			usuario=usuario["email"],
			fecha_visita=fecha_visita,
			cantidad=cantidad,
			edades=edades,
			tipo_de_pase=tipo_de_pase,
			forma_de_pago=forma_de_pago,
			email=str(email),
			notificador=notificador,
		)
		error = None
	except (PermissionError, ValueError) as excepcion:
		resultado = None
		error = str(excepcion)

	return templates.TemplateResponse(
		request=request,
		name="compra.html",
		context={"error": error, "resultado": resultado, "usuario": usuario},
		status_code=400 if error else 200,
	)
