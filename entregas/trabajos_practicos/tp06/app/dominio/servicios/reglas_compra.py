from datetime import date


def calcular_total(cantidad: int, tipo_de_pase: str) -> int:
	"""Calcula el total con los precios oficiales de cada pase."""
	precios = {"regular": 10000, "vip": 20000}
	if tipo_de_pase not in precios:
		raise ValueError("El tipo de pase no es valido")
	return cantidad * precios[tipo_de_pase]


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
	fecha_actual: date | None = None,
) -> None:
	"""Valida que la fecha sea actual o futura y corresponda a una apertura."""
	if fecha_actual is not None and fecha_visita < fecha_actual:
		raise ValueError("La fecha no puede ser anterior al dia actual")
	if dias_abiertos is not None and fecha_visita not in dias_abiertos:
		raise ValueError("El parque esta cerrado en la fecha seleccionada")
	if dias_abiertos is None and not es_dia_abierto(fecha_visita):
		raise ValueError("El parque esta cerrado en la fecha seleccionada")


def validar_tipo_pase(tipo_de_pase: str) -> None:
	"""Valida que el pase sea regular o VIP."""
	if tipo_de_pase not in {"regular", "vip"}:
		raise ValueError("El tipo de pase no es valido")


def validar_forma_pago(forma_de_pago: str) -> None:
	"""Valida que el pago sea en efectivo o con tarjeta."""
	if forma_de_pago not in {"efectivo", "tarjeta"}:
		raise ValueError("La forma de pago no es valida")
