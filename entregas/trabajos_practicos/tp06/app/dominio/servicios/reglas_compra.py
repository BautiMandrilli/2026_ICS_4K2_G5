from datetime import date


def validar_cantidad(cantidad: int) -> None:
	"""Valida que la cantidad de entradas este entre 1 y 10."""
	if cantidad < 1:
		raise ValueError("Debe comprar al menos una entrada")
	if cantidad > 10:
		raise ValueError("La cantidad maxima es de 10 entradas")


def validar_fecha_visita(
	fecha_visita: date,
	dias_abiertos: set[date],
	fecha_actual: date | None = None,
) -> None:
	"""Valida que la fecha sea actual o futura y corresponda a una apertura."""
	if fecha_actual is not None and fecha_visita < fecha_actual:
		raise ValueError("La fecha no puede ser anterior al dia actual")
	if fecha_visita not in dias_abiertos:
		raise ValueError("El parque esta cerrado en la fecha seleccionada")
