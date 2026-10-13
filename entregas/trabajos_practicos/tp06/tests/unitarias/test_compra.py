from datetime import date, timedelta

import pytest

from app.dominio.servicios.reglas_compra import validar_cantidad, validar_fecha_visita


def test_rechaza_mas_de_diez_entradas():
	# Criterio de aceptacion: la cantidad de entradas no puede superar 10.
	with pytest.raises(ValueError):
		validar_cantidad(11)


def test_rechaza_cero_entradas():
	# Criterio de aceptacion: debe comprarse al menos una entrada.
	with pytest.raises(ValueError):
		validar_cantidad(0)


def test_rechaza_fecha_con_parque_cerrado():
	# Criterio de aceptacion: la visita debe ser en un dia de apertura.
	hoy = date.today()
	fecha_cerrada = hoy + timedelta(days=2)

	with pytest.raises(ValueError):
		validar_fecha_visita(fecha_cerrada, {hoy})
