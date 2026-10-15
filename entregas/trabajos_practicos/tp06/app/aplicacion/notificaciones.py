from typing import Protocol


class ErrorNotificacion(Exception):
    """El correo no pudo entregarse al servidor de envio."""


class NotificadorCompra(Protocol):
    def enviar_confirmacion(self, destinatario: str, compra: dict) -> None:
        """Envia el resumen o lanza ErrorNotificacion."""
