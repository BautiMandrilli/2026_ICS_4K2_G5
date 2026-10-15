from datetime import date

from app.dominio.servicios.reglas_compra import (
	calcular_total,
	validar_cantidad,
	validar_edades,
	validar_fecha_visita,
	validar_forma_pago,
	validar_tipo_pase,
)


def comprar_entradas(
	usuario: str | None,
	fecha_visita: date,
	cantidad: int,
	edades: list[int],
	tipo_de_pase: str,
	forma_de_pago: str,
	dias_abiertos: set[date] | None = None,
	fecha_actual: date | None = None,
) -> dict:
	"""Coordina las validaciones necesarias para confirmar una compra."""
	if not usuario:
		raise PermissionError("El visitante debe estar registrado")

	validar_cantidad(cantidad)
	validar_edades(cantidad, edades)
	validar_fecha_visita(
		fecha_visita,
		dias_abiertos,
		fecha_actual or date.today(),
	)
	validar_tipo_pase(tipo_de_pase)
	validar_forma_pago(forma_de_pago)
	total = calcular_total(cantidad, tipo_de_pase)

	return {
		"estado": "confirmada",
		"usuario": usuario,
		"fecha": fecha_visita,
		"cantidad": cantidad,
		"tipo_de_pase": tipo_de_pase,
		"forma_de_pago": forma_de_pago,
		"total": total,
	}
