from __future__ import annotations

from collections import defaultdict
from datetime import date


class RepositorioComprasEnMemoria:
	"""Guarda en memoria cuantas entradas compro cada usuario por fecha."""

	def __init__(self) -> None:
		self._entradas: dict[tuple[str, date], int] = defaultdict(int)

	def entradas_compradas(self, usuario: str, fecha: date) -> int:
		return self._entradas[(usuario, fecha)]

	def registrar(self, usuario: str, fecha: date, cantidad: int) -> None:
		self._entradas[(usuario, fecha)] += cantidad