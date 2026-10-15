from datetime import date, timedelta

import pytest

from app.dominio.servicios.reglas_compra import (
	validar_cantidad,
	validar_edades,
	validar_fecha_visita,
	validar_forma_pago,
	validar_tipo_pase,
)


def test_rechaza_mas_de_diez_entradas():
	# Criterio de aceptacion: la cantidad de entradas no puede superar 10.
	with pytest.raises(ValueError):
		validar_cantidad(11)


def test_rechaza_cero_entradas():
	# Criterio de aceptacion: debe comprarse al menos una entrada.
	with pytest.raises(ValueError):
		validar_cantidad(0)


def test_permite_exactamente_diez_entradas():
	validar_cantidad(10)


def test_rechaza_cantidad_negativa():
	with pytest.raises(ValueError):
		validar_cantidad(-1)


def test_rechaza_fecha_con_parque_cerrado():
	# Criterio de aceptacion: la visita debe ser en un dia de apertura.
	hoy = date.today()
	fecha_cerrada = hoy + timedelta(days=2)

	with pytest.raises(ValueError):
		validar_fecha_visita(fecha_cerrada, {hoy})


def test_rechaza_fecha_anterior_al_dia_actual():
	# Criterio de aceptacion: la visita puede ser hoy o en una fecha futura.
	hoy = date.today()
	fecha_anterior = hoy - timedelta(days=1)

	with pytest.raises(ValueError):
		validar_fecha_visita(fecha_anterior, {fecha_anterior, hoy}, hoy)


def test_permite_fecha_actual_si_el_parque_esta_abierto():
	hoy = date.today()

	validar_fecha_visita(hoy, {hoy}, hoy)


def test_permite_fecha_futura_si_el_parque_esta_abierto():
	hoy = date.today()
	fecha_futura = hoy + timedelta(days=2)

	validar_fecha_visita(fecha_futura, {hoy, fecha_futura}, hoy)


def test_rechaza_visita_un_lunes():
	# Regla del parque: los lunes permanece cerrado.
	lunes = date(2026, 10, 19)

	with pytest.raises(ValueError):
		validar_fecha_visita(lunes)


def test_rechaza_visita_el_25_de_diciembre():
	# Regla del parque: el 25 de diciembre permanece cerrado.
	navidad = date(2026, 12, 25)

	with pytest.raises(ValueError):
		validar_fecha_visita(navidad)


def test_rechaza_visita_el_1_de_enero():
	# Regla del parque: el 1 de enero permanece cerrado.
	comienzo_de_anio = date(2027, 1, 1)

	with pytest.raises(ValueError):
		validar_fecha_visita(comienzo_de_anio)


def test_permite_visita_un_martes():
	martes = date(2026, 10, 20)

	validar_fecha_visita(martes)


def test_rechaza_tipo_de_pase_invalido():
	# Criterio de aceptacion: el pase debe ser regular o VIP.
	with pytest.raises(ValueError):
		validar_tipo_pase("premium")


def test_permite_tipo_de_pase_regular():
	validar_tipo_pase("regular")


def test_permite_tipo_de_pase_vip():
	validar_tipo_pase("vip")


def test_rechaza_forma_de_pago_invalida():
	# Criterio de aceptacion: debe seleccionarse efectivo o tarjeta.
	with pytest.raises(ValueError):
		validar_forma_pago("transferencia")


def test_permite_pago_en_efectivo():
	validar_forma_pago("efectivo")


def test_permite_pago_con_tarjeta():
	validar_forma_pago("tarjeta")


def test_rechaza_forma_de_pago_vacia():
	with pytest.raises(ValueError):
		validar_forma_pago("")


def test_rechaza_tipo_de_pase_vacio():
	with pytest.raises(ValueError):
		validar_tipo_pase("")


def test_rechaza_compra_sin_edades():
	# Criterio de aceptacion: debe indicarse la edad de cada visitante.
	with pytest.raises(ValueError):
		validar_edades(1, [])


def test_rechaza_menos_edades_que_entradas():
	with pytest.raises(ValueError):
		validar_edades(3, [20, 30])


def test_rechaza_mas_edades_que_entradas():
	with pytest.raises(ValueError):
		validar_edades(1, [20, 30])


def test_permite_una_edad_por_entrada():
	validar_edades(2, [20, 30])
