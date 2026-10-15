import math
import os
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

from dotenv import load_dotenv

from app.aplicacion.notificaciones import ErrorNotificacion


RUTA_ENV = Path(__file__).resolve().parents[2] / ".env"


@dataclass(frozen=True)
class NotificadorSMTP:
    host: str
    puerto: int
    usuario: str
    password: str
    nombre: str
    timeout: float

    def enviar_confirmacion(self, destinatario: str, compra: dict) -> None:
        if not self.usuario or not self.password:
            raise ErrorNotificacion("Faltan credenciales SMTP")

        try:
            mensaje = EmailMessage()
            mensaje["Subject"] = "Confirmación de compra | EcoHarmony Park"
            mensaje["From"] = formataddr((self.nombre, self.usuario))
            mensaje["To"] = destinatario
            mensaje.set_content(
                "Tu compra está confirmada.\n\n"
                f"Fecha de visita: {compra['fecha']}\n"
                f"Entradas: {compra['cantidad']}\n"
                f"Tipo de pase: {compra['tipo_de_pase']}\n"
                f"Total: ${compra['total']}\n\n"
                "Recordá abonar en boletería al ingresar al parque.\n"
            )
            with smtplib.SMTP(self.host, self.puerto, timeout=self.timeout) as smtp:
                smtp.ehlo()
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
                smtp.login(self.usuario, self.password)
                rechazados = smtp.send_message(mensaje)
                if rechazados:
                    raise ErrorNotificacion("Destinatario rechazado")
        except (smtplib.SMTPException, OSError, ValueError) as error:
            raise ErrorNotificacion("No se pudo enviar el correo") from error


def obtener_notificador() -> NotificadorSMTP:
    load_dotenv(RUTA_ENV, override=False)
    try:
        puerto = int(os.getenv("SMTP_PORT", "587"))
        timeout = float(os.getenv("SMTP_TIMEOUT", "10"))
        if not 1 <= puerto <= 65535 or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Puerto o timeout invalido")
        return NotificadorSMTP(
            host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            puerto=puerto,
            usuario=os.getenv("SMTP_USER", "").strip(),
            password=os.getenv("SMTP_PASSWORD", ""),
            nombre=os.getenv("SMTP_FROM_NAME", "EcoHarmony Park"),
            timeout=timeout,
        )
    except ValueError as error:
        raise ErrorNotificacion("Configuracion SMTP invalida") from error
