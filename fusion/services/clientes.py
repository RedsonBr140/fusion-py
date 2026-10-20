from __future__ import annotations

from fusion import grid
from fusion.http import HttpSession
from fusion.models import Cliente, ClientesPage

GET_CLIENTES_PATH = "/php/cadastros/cliente/get_clientes.php"
REFERER_MENU = "cadcli"

# Confirmed filterable field from a captured request against the client
# registration grid. Other t16_/t44_/t62_/t04_ columns in the response may
# also be valid "campo" values but haven't been confirmed.
CAMPO_CODIGO_ERP = "t44_codigo_erp"


class ClientesService:
    def __init__(self, http: HttpSession):
        self._http = http

    def buscar(self, campo: str, valor: str, *, page: int = 1, rows: int = 10) -> ClientesPage:
        total, rows_data = grid.search(
            self._http, GET_CLIENTES_PATH, campo, valor, page=page, rows=rows,
            referer_menu=REFERER_MENU, params={"LGPD": 0},
        )
        return ClientesPage(total=total, rows=[Cliente.from_api(row) for row in rows_data])
