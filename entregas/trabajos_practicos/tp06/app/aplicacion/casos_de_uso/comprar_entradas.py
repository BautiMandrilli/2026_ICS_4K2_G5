from __future__ import annotations

from datetime import date, datetime
import logging

from app.aplicacion.notificaciones import ErrorNotificacion, NotificadorCompra

from app.infraestructura.base_de_datos.compras import RepositorioComprasEnMemoria

from app.dominio.servicios.reglas_compra import (
	calcular_total,
	validar_acumulado,
	validar_cantidad,
	validar_edades,
	validar_fecha_visita,
	validar_forma_pago,
	validar_tipo_pase,
)


logger = logging.getLogger(__name__)


def validar_compra(
	usuario: str | None,
	fecha_visita: date,
	cantidad: int,
	edades: list[int],
	tipo_de_pase: str,
	forma_de_pago: str,
	dias_abiertos: set[date] | None = None,
	ahora: datetime | None = None,
	repositorio: RepositorioComprasEnMemoria | None = None,
) -> None:
	"""Aplica todas las reglas de compra sin registrar nada."""
	if not usuario:
		raise PermissionError("El visitante debe estar registrado")

	validar_cantidad(cantidad)
	validar_edades(cantidad, edades)
	validar_fecha_visita(
		fecha_visita,
		dias_abiertos,
		ahora or datetime.now(),
	)
	validar_tipo_pase(tipo_de_pase)
	validar_forma_pago(forma_de_pago)
	if repositorio is not None:
		validar_acumulado(repositorio.entradas_compradas(usuario, fecha_visita), cantidad)


def comprar_entradas(
	usuario: str | None,
	fecha_visita: date,
	cantidad: int,
	edades: list[int],
	tipo_de_pase: str,
	forma_de_pago: str,
	dias_abiertos: set[date] | None = None,
	ahora: datetime | None = None,
	email: str | None = None,
	notificador: NotificadorCompra | None = None,
	repositorio: RepositorioComprasEnMemoria | None = None,
) -> dict:
	"""Coordina las validaciones necesarias para confirmar una compra."""
	validar_compra(
		usuario,
		fecha_visita,
		cantidad,
		edades,
		tipo_de_pase,
		forma_de_pago,
		dias_abiertos,
		ahora,
		repositorio,
	)
	total = calcular_total(cantidad, tipo_de_pase, edades)

	if repositorio is not None:
		repositorio.registrar(usuario, fecha_visita, cantidad)
	resultado = {
		"estado": "confirmada",
		"usuario": usuario,
		"fecha": fecha_visita,
		"cantidad": cantidad,
		"tipo_de_pase": tipo_de_pase,
		"forma_de_pago": forma_de_pago,
		"total": total,
		"correo_estado": "omitido",
	}
	if email:
		resultado["correo_estado"] = "fallido"
		try:
			if notificador is None:
				raise ErrorNotificacion("No hay notificador configurado")
			notificador.enviar_confirmacion(email, resultado)
			resultado["correo_estado"] = "enviado"
		except ErrorNotificacion:
			logger.warning("No se pudo enviar la confirmacion de compra por correo")
	return resultado