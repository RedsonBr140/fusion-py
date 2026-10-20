from __future__ import annotations

from fusion import grid
from fusion.http import HttpSession
from fusion.models import Motorista, MotoristasPage

GET_MOTORISTAS_PATH = "/php/cadastros/motorista/get_motoristas.php"
# Guessed from the "cadcli" convention seen on the clients grid — unconfirmed,
# but the server doesn't appear to validate Referer content.
REFERER_MENU = "cadmot"
# ?LGPD=0 was confirmed on the clients grid; carried over here on the
# assumption it's the convention for any screen showing personal data
# (drivers have CPF), but never independently confirmed for this endpoint.

# Confirmed filterable fields.
CAMPO_NOME = "t05_nome"
CAMPO_CODIGO_ERP = "t05_codigo_erp"


class MotoristasService:
    def __init__(self, http: HttpSession):
        self._http = http

    def buscar(self, campo: str, valor: str, *, page: int = 1, rows: int = 10) -> MotoristasPage:
        total, rows_data = grid.search(
            self._http, GET_MOTORISTAS_PATH, campo, valor, page=page, rows=rows,
            referer_menu=REFERER_MENU, params={"LGPD": 0},
        )
        return MotoristasPage(total=total, rows=[Motorista.from_api(row) for row in rows_data])
