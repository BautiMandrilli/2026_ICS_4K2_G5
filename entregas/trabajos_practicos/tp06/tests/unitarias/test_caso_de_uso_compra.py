from datetime import date, datetime

import pytest

from app.aplicacion.casos_de_uso.comprar_entradas import comprar_entradas
from app.infraestructura.base_de_datos.compras import RepositorioComprasEnMemoria

def test_confirma_una_compra_valida():
    resultado = comprar_entradas(
        usuario="visitante_registrado",
        fecha_visita=date(2026, 10, 20),
        cantidad=2,
        edades=[25, 30],
        tipo_de_pase="regular",
        forma_de_pago="efectivo",
        ahora=datetime(2026, 10, 14, 10, 0),
    )

    assert resultado["estado"] == "confirmada"
    assert resultado["cantidad"] == 2
    assert resultado["fecha"] == date(2026, 10, 20)


def test_rechaza_compra_con_mas_de_diez_entradas():
    with pytest.raises(ValueError):
        comprar_entradas(
            usuario="visitante_registrado",
            fecha_visita=date(2026, 10, 20),
            cantidad=11,
            edades=[25] * 11,
            tipo_de_pase="regular",
            forma_de_pago="efectivo",
            ahora=datetime(2026, 10, 14, 10, 0),
        )


def test_rechaza_compra_si_el_acumulado_de_la_fecha_supera_diez():
    repositorio = RepositorioComprasEnMemoria()
    datos = dict(
        usuario="visitante_registrado",
        fecha_visita=date(2026, 10, 20),
        tipo_de_pase="regular",
        forma_de_pago="efectivo",
        ahora=datetime(2026, 10, 14, 10, 0),
        repositorio=repositorio,
    )
    comprar_entradas(cantidad=6, edades=[25] * 6, **datos)

    with pytest.raises(ValueError):
        comprar_entradas(cantidad=5, edades=[25] * 5, **datos)