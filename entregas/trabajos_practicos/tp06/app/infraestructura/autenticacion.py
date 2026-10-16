from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
import sqlite3

from fastapi import Depends, HTTPException, Request
from pwdlib import PasswordHash

from app.infraestructura.base_de_datos.usuarios import obtener_conexion


NOMBRE_COOKIE_SESION = "eco_session"
DURACION_SESION_SEGUNDOS = 8 * 60 * 60
CLAVE_FIRMA_SESION = os.getenv("SESSION_SECRET_KEY") or secrets.token_urlsafe(32)
hash_contrasenas = PasswordHash.recommended()


def registrar_usuario(conexion: sqlite3.Connection, email: str, contrasena: str) -> int:
	contrasena_hash = hash_contrasenas.hash(contrasena)
	cursor = conexion.execute(
		"INSERT INTO usuarios (email, password_hash) VALUES (?, ?)",
		(email.strip().lower(), contrasena_hash),
	)
	conexion.commit()
	return int(cursor.lastrowid)


def autenticar_usuario(
	conexion: sqlite3.Connection,
	email: str,
	contrasena: str,
) -> dict | None:
	usuario = conexion.execute(
		"SELECT id, email, password_hash FROM usuarios WHERE email = ? COLLATE NOCASE",
		(email.strip(),),
	).fetchone()
	if usuario is None:
		return None
	if not hash_contrasenas.verify(contrasena, usuario["password_hash"]):
		return None
	return {"id": int(usuario["id"]), "email": usuario["email"]}


def _codificar_url(datos: bytes) -> str:
	return base64.urlsafe_b64encode(datos).rstrip(b"=").decode("ascii")


def _decodificar_url(datos: str) -> bytes:
	return base64.urlsafe_b64decode(datos + "=" * (-len(datos) % 4))


def crear_token_sesion(usuario_id: int) -> str:
	contenido = json.dumps(
		{
			"uid": usuario_id,
			"exp": int(time.time()) + DURACION_SESION_SEGUNDOS,
		},
		separators=(",", ":"),
	).encode("utf-8")
	contenido_codificado = _codificar_url(contenido)
	firma = hmac.new(
		CLAVE_FIRMA_SESION.encode("utf-8"),
		contenido_codificado.encode("ascii"),
		hashlib.sha256,
	).digest()
	return f"{contenido_codificado}.{_codificar_url(firma)}"


def leer_token_sesion(token: str | None) -> int | None:
	if not token:
		return None
	try:
		contenido_codificado, firma_recibida = token.split(".", maxsplit=1)
		firma_esperada = hmac.new(
			CLAVE_FIRMA_SESION.encode("utf-8"),
			contenido_codificado.encode("ascii"),
			hashlib.sha256,
		).digest()
		if not hmac.compare_digest(_decodificar_url(firma_recibida), firma_esperada):
			return None
		contenido = json.loads(_decodificar_url(contenido_codificado))
		usuario_id = contenido.get("uid")
		if type(usuario_id) is not int or usuario_id < 1:
			return None
		if type(contenido.get("exp")) is not int or contenido["exp"] < int(time.time()):
			return None
		return usuario_id
	except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
		return None


def usuario_actual_opcional(
	request: Request,
	conexion: sqlite3.Connection = Depends(obtener_conexion),
) -> dict | None:
	usuario_id = leer_token_sesion(request.cookies.get(NOMBRE_COOKIE_SESION))
	if usuario_id is None:
		return None
	usuario = conexion.execute(
		"SELECT id, email FROM usuarios WHERE id = ?",
		(usuario_id,),
	).fetchone()
	if usuario is None:
		return None
	return {"id": int(usuario["id"]), "email": usuario["email"]}


def usuario_actual(
	usuario: dict | None = Depends(usuario_actual_opcional),
) -> dict:
	if usuario is None:
		raise HTTPException(status_code=303, headers={"Location": "/login"})
	return usuario


def establecer_cookie_sesion(response, request: Request, usuario_id: int) -> None:
	response.set_cookie(
		key=NOMBRE_COOKIE_SESION,
		value=crear_token_sesion(usuario_id),
		max_age=DURACION_SESION_SEGUNDOS,
		httponly=True,
		secure=request.url.scheme == "https",
		samesite="lax",
		path="/",
	)
