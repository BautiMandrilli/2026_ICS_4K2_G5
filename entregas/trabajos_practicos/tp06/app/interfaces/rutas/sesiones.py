import sqlite3
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from pydantic import EmailStr
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.infraestructura.autenticacion import (
	autenticar_usuario,
	establecer_cookie_sesion,
	registrar_usuario,
)
from app.infraestructura.base_de_datos.usuarios import obtener_conexion


router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "plantillas")


def pagina_sesion(request: Request, plantilla: str, error: str, status_code: int):
	return templates.TemplateResponse(
		request=request,
		name=plantilla,
		context={"error": error},
		status_code=status_code,
	)


@router.get("/login", response_class=HTMLResponse)
def mostrar_login(request: Request):
	return pagina_sesion(request, "login.html", "", 200)


@router.post("/login", response_class=HTMLResponse)
def iniciar_sesion(
	request: Request,
	email: EmailStr = Form(...),
	contrasena: str = Form(...),
	conexion: sqlite3.Connection = Depends(obtener_conexion),
):
	usuario = autenticar_usuario(conexion, str(email), contrasena)
	if usuario is None:
		return pagina_sesion(
			request,
			"login.html",
			"El correo o la contraseña no son correctos.",
			401,
		)
	respuesta = RedirectResponse("/", status_code=303)
	establecer_cookie_sesion(respuesta, request, usuario["id"])
	return respuesta


@router.get("/registro", response_class=HTMLResponse)
def mostrar_registro(request: Request):
	return pagina_sesion(request, "registro.html", "", 200)


@router.post("/registro", response_class=HTMLResponse)
def crear_cuenta(
	request: Request,
	email: EmailStr = Form(...),
	contrasena: str = Form(...),
	conexion: sqlite3.Connection = Depends(obtener_conexion),
):
	if len(contrasena) < 8:
		return pagina_sesion(
			request,
			"registro.html",
			"La contraseña debe tener al menos 8 caracteres.",
			400,
		)
	if len(contrasena) > 128:
		return pagina_sesion(
			request,
			"registro.html",
			"La contraseña no puede superar los 128 caracteres.",
			400,
		)
	try:
		usuario_id = registrar_usuario(conexion, str(email), contrasena)
	except sqlite3.IntegrityError:
		conexion.rollback()
		return pagina_sesion(
			request,
			"registro.html",
			"Ya existe una cuenta con ese correo.",
			409,
		)
	respuesta = RedirectResponse("/", status_code=303)
	establecer_cookie_sesion(respuesta, request, usuario_id)
	return respuesta


@router.post("/logout")
def cerrar_sesion(request: Request):
	respuesta = RedirectResponse("/login", status_code=303)
	respuesta.delete_cookie(
		key="eco_session",
		path="/",
		httponly=True,
		secure=request.url.scheme == "https",
		samesite="lax",
	)
	return respuesta
