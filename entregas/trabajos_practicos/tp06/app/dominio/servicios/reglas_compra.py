from __future__ import annotations

from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta

MESES_MAXIMOS_ANTICIPACION = 1
HORA_LIMITE_COMPRA_MISMO_DIA = time(17, 30)

def calcular_total(
	cantidad: int,
	tipo_de_pase: str,
	edades: list[int] | None = None,
) -> int:
	"""Calcula el total aplicando descuentos segun la edad."""
	precios = {"regular": 10000, "vip": 20000}
	if tipo_de_pase not in precios:
		raise ValueError("El tipo de pase no es valido")

	precio = precios[tipo_de_pase]
	if edades is None:
		return cantidad * precio

	if len(edades) != cantidad:
		raise ValueError("Debe indicar la edad de cada visitante")

	total = 0
	for edad in edades:
		if edad <= 3:
			total += 0
		elif edad <= 15 or edad >= 60:
			total += precio // 2
		else:
			total += precio
	return total


def es_dia_abierto(fecha: date) -> bool:
	"""Indica si el parque abre segun su calendario oficial."""
	es_lunes = fecha.weekday() == 0
	es_feriado = (fecha.month, fecha.day) in {(1, 1), (12, 25)}
	return not es_lunes and not es_feriado


def validar_cantidad(cantidad: int) -> None:
	"""Valida que la cantidad de entradas este entre 1 y 10."""
	if cantidad < 1:
		raise ValueError("Debe comprar al menos una entrada")
	if cantidad > 10:
		raise ValueError("La cantidad maxima es de 10 entradas")


def validar_edades(cantidad: int, edades: list[int]) -> None:
	"""Valida que haya una edad entre 0 y 120 por cada entrada."""
	if len(edades) != cantidad:
		raise ValueError("Debe indicar la edad de cada visitante")
	if any(edad < 0 or edad > 120 for edad in edades):
		raise ValueError("La edad debe estar entre 0 y 120")


def validar_fecha_visita(
	fecha_visita: date,
	dias_abiertos: set[date] | None = None,
	ahora: datetime | None = None,
) -> None:
	"""Valida que la fecha sea actual o futura y corresponda a una apertura."""
	fecha_actual = ahora.date() if ahora is not None else None
	if ahora is not None and fecha_visita < fecha_actual:
		raise ValueError("La fecha no puede ser anterior al dia actual")
	if fecha_actual is not None:
		limite = fecha_actual + relativedelta(months=MESES_MAXIMOS_ANTICIPACION)
		if fecha_visita > limite:
			raise ValueError("La fecha no puede superar un mes de anticipacion")
	es_visita_de_hoy = fecha_visita == fecha_actual
	if ahora is not None and es_visita_de_hoy and ahora.time() > HORA_LIMITE_COMPRA_MISMO_DIA:
		raise ValueError("La compra de entrada para el mismo día se cierra a las 17:30")
	if dias_abiertos is not None and fecha_visita not in dias_abiertos:
		raise ValueError("El parque esta cerrado en la fecha seleccionada")
	if dias_abiertos is None and not es_dia_abierto(fecha_visita):
		raise ValueError("El parque esta cerrado en la fecha seleccionada")


def validar_tipo_pase(tipo_de_pase: str) -> None:
	"""Valida que el pase sea regular o VIP."""
	if tipo_de_pase not in {"regular", "vip"}:
		raise ValueError("El tipo de pase no es valido")


def validar_forma_pago(forma_de_pago: str) -> None:
	"""Valida que el pago sea en efectivo, tarjeta o Mercado Pago."""
	if forma_de_pago not in {"efectivo", "tarjeta", "mercadopago"}:
		raise ValueError("La forma de pago no es valida")
