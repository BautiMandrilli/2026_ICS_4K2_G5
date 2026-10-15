import os
import sqlite3
from pathlib import Path


RUTA_BASE_DATOS = Path(
	os.getenv(
		"TP6_DATABASE_PATH",
		Path(__file__).resolve().parents[2] / "usuarios.db",
	)
)


def inicializar_base_de_datos() -> None:
	RUTA_BASE_DATOS.parent.mkdir(parents=True, exist_ok=True)
	with sqlite3.connect(RUTA_BASE_DATOS, timeout=10) as conexion:
		conexion.execute(
			"""
			CREATE TABLE IF NOT EXISTS usuarios (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				email TEXT NOT NULL COLLATE NOCASE UNIQUE,
				password_hash TEXT NOT NULL,
				creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
			)
			"""
		)
def obtener_conexion():
	RUTA_BASE_DATOS.parent.mkdir(parents=True, exist_ok=True)
	conexion = sqlite3.connect(RUTA_BASE_DATOS, timeout=10)
	conexion.row_factory = sqlite3.Row
	try:
		yield conexion
	finally:
		conexion.close()
