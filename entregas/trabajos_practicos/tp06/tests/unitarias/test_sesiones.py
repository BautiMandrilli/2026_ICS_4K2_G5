import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.infraestructura.base_de_datos import usuarios as base_de_datos
from app.main import app


@pytest.fixture
def cliente(tmp_path, monkeypatch):
	monkeypatch.setattr(base_de_datos, "RUTA_BASE_DATOS", tmp_path / "usuarios.db")
	with TestClient(app, follow_redirects=False) as test_client:
		yield test_client


def datos_registro(**cambios):
	datos = {"email": "visitante@example.com", "contrasena": "clave-segura-123"}
	datos.update(cambios)
	return datos


def test_compra_y_pagina_principal_requieren_sesion(cliente):
	assert cliente.get("/").status_code == 303
	assert cliente.get("/").headers["location"] == "/login"

	respuesta = cliente.post(
		"/compras",
		data={
			"fecha_visita": "2099-10-15",
			"cantidad": "1",
			"edades": "25",
			"tipo_de_pase": "regular",
			"forma_de_pago": "efectivo",
			"email": "visitante@example.com",
		},
	)
	assert respuesta.status_code == 303
	assert respuesta.headers["location"] == "/login"


def test_registro_crea_cuenta_con_contrasena_hasheada_y_abre_sesion(cliente):
	respuesta = cliente.post("/registro", data=datos_registro())
	assert respuesta.status_code == 303
	assert respuesta.headers["location"] == "/"
	assert "eco_session=" in respuesta.headers["set-cookie"]
	assert "httponly" in respuesta.headers["set-cookie"].lower()

	with sqlite3.connect(base_de_datos.RUTA_BASE_DATOS) as conexion:
		usuario = conexion.execute(
			"SELECT email, password_hash FROM usuarios"
		).fetchone()
	assert usuario[0] == "visitante@example.com"
	assert usuario[1] != "clave-segura-123"
	assert usuario[1].startswith("$argon2")

	pagina = cliente.get("/")
	assert pagina.status_code == 200
	assert "Comprar entradas" in pagina.text
	assert "visitante@example.com" in pagina.text


def test_login_cierra_sesion_y_vuelve_a_aceptar_credenciales(cliente):
	cliente.post("/registro", data=datos_registro())
	cliente.post("/logout")
	assert cliente.get("/").status_code == 303

	respuesta = cliente.post(
		"/login",
		data={"email": "VISITANTE@example.com", "contrasena": "clave-segura-123"},
	)
	assert respuesta.status_code == 303
	assert cliente.get("/").status_code == 200

	cliente.post("/logout")
	assert cliente.get("/").status_code == 303


def test_login_rechaza_contrasena_incorrecta(cliente):
	cliente.post("/registro", data=datos_registro())
	cliente.post("/logout")

	respuesta = cliente.post(
		"/login",
		data={"email": "visitante@example.com", "contrasena": "incorrecta"},
	)
	assert respuesta.status_code == 401
	assert "no son correctos" in respuesta.text
	assert cliente.get("/").status_code == 303


def test_registro_rechaza_contrasena_corta_y_email_duplicado(cliente):
	respuesta = cliente.post(
		"/registro",
		data=datos_registro(contrasena="corta"),
	)
	assert respuesta.status_code == 400
	assert "al menos 8 caracteres" in respuesta.text

	cliente.post("/registro", data=datos_registro())
	cliente.post("/logout")
	duplicada = cliente.post(
		"/registro",
		data=datos_registro(email="VISITANTE@example.com"),
	)
	assert duplicada.status_code == 409
	assert "Ya existe una cuenta" in duplicada.text
