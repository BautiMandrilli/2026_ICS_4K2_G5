from datetime import date, timedelta
from unittest.mock import Mock, patch
import os
import smtplib
import ssl

import pytest
from fastapi.testclient import TestClient

from app.aplicacion.casos_de_uso.comprar_entradas import comprar_entradas
from app.aplicacion.notificaciones import ErrorNotificacion
from app.infraestructura.base_de_datos import usuarios as base_de_datos
from app.infraestructura.notificaciones import correo
from app.interfaces.rutas.compras import notificador_compra
from app.main import app


@pytest.fixture
def datos():
    return dict(
        usuario="visitante", fecha_visita=date(2030, 10, 15), cantidad=2,
        edades=[25, 30], tipo_de_pase="regular", forma_de_pago="efectivo",
        fecha_actual=date(2030, 10, 14),
    )


@pytest.fixture
def smtp_config():
    return correo.NotificadorSMTP(
        "smtp.gmail.com", 587, "parque@gmail.com", "secreto", "EcoHarmony Park", 10,
    )


def test_smtp_envia_resumen_con_tls(datos, smtp_config):
    compra = comprar_entradas(**datos)
    with patch.object(correo.smtplib, "SMTP") as constructor:
        smtp = constructor.return_value.__enter__.return_value
        smtp.send_message.return_value = {}
        smtp_config.enviar_confirmacion("cliente@example.com", compra)

    constructor.assert_called_once_with("smtp.gmail.com", 587, timeout=10)
    assert [c[0] for c in smtp.method_calls] == [
        "ehlo", "starttls", "ehlo", "login", "send_message",
    ]
    contexto = smtp.starttls.call_args.kwargs["context"]
    assert contexto.check_hostname
    assert contexto.verify_mode == ssl.CERT_REQUIRED
    smtp.login.assert_called_once_with("parque@gmail.com", "secreto")
    mensaje = smtp.send_message.call_args.args[0]
    assert mensaje["To"] == "cliente@example.com"
    assert mensaje["From"] == "EcoHarmony Park <parque@gmail.com>"
    contenido = mensaje.get_content()
    for texto in ("2030-10-15", "Entradas: 2", "regular", "$20000", "boletería"):
        assert texto in contenido


def test_caso_de_uso_envia_solo_compra_valida(datos):
    notificador = Mock()
    resultado = comprar_entradas(**datos, email="cliente@example.com", notificador=notificador)
    assert resultado["correo_estado"] == "enviado"
    notificador.enviar_confirmacion.assert_called_once_with("cliente@example.com", resultado)
    notificador.reset_mock()
    with pytest.raises(ValueError):
        comprar_entradas(**{**datos, "cantidad": 11}, email="cliente@example.com", notificador=notificador)
    notificador.enviar_confirmacion.assert_not_called()
    assert comprar_entradas(**datos)["correo_estado"] == "omitido"


@pytest.mark.parametrize("error", [
    smtplib.SMTPAuthenticationError(535, b"secreto"),
    TimeoutError("secreto"),
    smtplib.SMTPNotSupportedError("STARTTLS no disponible"),
])
def test_fallo_smtp_conserva_compra_sin_exponer_secretos(datos, smtp_config, error, caplog):
    with patch.object(correo.smtplib, "SMTP", side_effect=error) as constructor:
        resultado = comprar_entradas(**datos, email="cliente@example.com", notificador=smtp_config)
    assert resultado["estado"] == "confirmada"
    assert resultado["correo_estado"] == "fallido"
    constructor.assert_called_once()
    assert "secreto" not in caplog.text


def test_sin_credenciales_no_conecta(datos):
    notificador = correo.NotificadorSMTP("smtp.gmail.com", 587, "", "", "Parque", 10)
    with patch.object(correo.smtplib, "SMTP") as constructor:
        resultado = comprar_entradas(**datos, email="cliente@example.com", notificador=notificador)
    assert resultado["estado"] == "confirmada"
    assert resultado["correo_estado"] == "fallido"
    constructor.assert_not_called()


def test_rechazo_de_destinatario(datos, smtp_config):
    with patch.object(correo.smtplib, "SMTP") as constructor:
        smtp = constructor.return_value.__enter__.return_value
        smtp.send_message.return_value = {"cliente@example.com": (550, b"rechazado")}
        with pytest.raises(ErrorNotificacion):
            smtp_config.enviar_confirmacion("cliente@example.com", comprar_entradas(**datos))


def test_env_ruta_independiente_y_prioridad(tmp_path, monkeypatch):
    assert correo.RUTA_ENV == correo.Path(correo.__file__).resolve().parents[2] / ".env"
    ruta = tmp_path / "app" / ".env"
    ruta.parent.mkdir()
    ruta.write_text("SMTP_USER=archivo@gmail.com\nSMTP_PASSWORD=archivo\nSMTP_PORT=587\n", encoding="utf-8")
    with patch.dict(os.environ, {}, clear=True):
        monkeypatch.setattr(correo, "RUTA_ENV", ruta)
        monkeypatch.chdir(tmp_path)
        os.environ["SMTP_USER"] = "sistema@gmail.com"
        notificador = correo.obtener_notificador()
        assert notificador.usuario == "sistema@gmail.com"
        assert notificador.password == "archivo"
        assert notificador.timeout == 10


@pytest.mark.parametrize("variable,valor", [("SMTP_PORT", "abc"), ("SMTP_TIMEOUT", "nan"), ("SMTP_TIMEOUT", "0")])
def test_configuracion_invalida_no_impide_comprar(variable, valor):
    with patch.dict(os.environ, {variable: valor}), patch.object(correo, "load_dotenv"):
        assert notificador_compra() is None


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    monkeypatch.setattr(base_de_datos, "RUTA_BASE_DATOS", tmp_path / "usuarios.db")
    notificador = Mock()
    app.dependency_overrides[notificador_compra] = lambda: notificador
    try:
        with TestClient(app) as client:
            client.post(
                "/registro",
                data={"email": "comprador@example.com", "contrasena": "clave-de-prueba-123"},
            )
            yield client, notificador
    finally:
        app.dependency_overrides.clear()


def proxima_fecha_abierta():
    dia = date.today() + timedelta(days=1)
    while dia.weekday() == 0 or (dia.month, dia.day) in {(1, 1), (12, 25)}:
        dia += timedelta(days=1)
    return dia


def formulario():
    return dict(fecha_visita=proxima_fecha_abierta().isoformat(), cantidad="1", edades="25",
                tipo_de_pase="regular", forma_de_pago="efectivo", email="cliente@example.com")


def test_formulario_pide_email(cliente):
    client, _ = cliente
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert 'name="email" type="email" autocomplete="email" required' in respuesta.text


@pytest.mark.parametrize("email", [None, "incorrecto", ""])
def test_ruta_rechaza_email_invalido_o_ausente(cliente, email):
    client, notificador = cliente
    datos = formulario()
    if email is None:
        datos.pop("email")
    else:
        datos["email"] = email
    assert client.post("/compras", data=datos).status_code == 422
    notificador.enviar_confirmacion.assert_not_called()


@pytest.mark.parametrize("falla", [False, True])
def test_ruta_confirma_y_muestra_estado_correo(cliente, falla):
    client, notificador = cliente
    if falla:
        notificador.enviar_confirmacion.side_effect = ErrorNotificacion("secreto")
    respuesta = client.post("/compras", data=formulario())
    assert respuesta.status_code == 200
    assert "Compra confirmada" in respuesta.text
    assert ("no hace falta repetir la compra" if falla else "Enviamos el resumen") in respuesta.text
    assert "secreto" not in respuesta.text
    notificador.enviar_confirmacion.assert_called_once()


def test_ruta_compra_invalida_no_envia(cliente):
    client, notificador = cliente
    respuesta = client.post("/compras", data={**formulario(), "cantidad": "11"})
    assert respuesta.status_code == 400
    notificador.enviar_confirmacion.assert_not_called()


def test_ruta_sin_configuracion_confirma_con_aviso(cliente):
    client, _ = cliente
    app.dependency_overrides[notificador_compra] = lambda: None
    respuesta = client.post("/compras", data=formulario())
    assert respuesta.status_code == 200
    assert "Compra confirmada" in respuesta.text
    assert "no hace falta repetir la compra" in respuesta.text
