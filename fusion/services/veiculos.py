from __future__ import annotations

from fusion import grid
from fusion.http import HttpSession
from fusion.models import Veiculo, VeiculosPage

GET_TRANSPORTES_PATH = "/php/cadastros/transporte/get_transportes.php"
REFERER_MENU = "cadvei"

# No campo filter was used in the captured request (it listed everything
# unfiltered with campo/valor empty) — no CAMPO_* constants confirmed yet.


class VeiculosService:
    def __init__(self, http: HttpSession):
        self._http = http

    def buscar(
        self, campo: str = "", valor: str = "", *, page: int = 1, rows: int = 10
    ) -> VeiculosPage:
        total, rows_data = grid.search(
            self._http, GET_TRANSPORTES_PATH, campo, valor, page=page, rows=rows,
            referer_menu=REFERER_MENU,
        )
        return VeiculosPage(total=total, rows=[Veiculo.from_api(row) for row in rows_data])
