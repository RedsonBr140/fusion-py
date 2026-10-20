from __future__ import annotations

import logging

from fusion.exceptions import FusionError
from fusion.http import HttpSession
from fusion.models import Cliente, ClientesPage

logger = logging.getLogger("fusion.clientes")

GET_CLIENTES_PATH = "/php/cadastros/cliente/get_clientes.php"

# Confirmed filterable field from a captured request against the client
# registration grid (menu=cadcli). Other t16_/t44_/t62_/t04_ columns in the
# response may also be valid "campo" values but haven't been confirmed.
CAMPO_CODIGO_ERP = "t44_codigo_erp"


class ClientesService:
    def __init__(self, http: HttpSession):
        self._http = http

    def buscar(self, campo: str, valor: str, *, page: int = 1, rows: int = 10) -> ClientesPage:
        logger.debug("Searching clients: %s=%s (page=%s, rows=%s)", campo, valor, page, rows)

        response = self._http.post(
            GET_CLIENTES_PATH,
            params={"LGPD": 0},
            data={"campo": campo, "valor": valor, "page": page, "rows": rows},
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self._http.config.base_url}/html/menus/main.php?menu=cadcli",
            },
        )

        data = response.json()
        if "rows" not in data:
            raise FusionError(f"Unexpected get_clientes response: {data}")

        # A no-match search returns total/rows as null rather than 0/[].
        total = data.get("total")
        rows = data.get("rows") or []

        return ClientesPage(
            total=int(total) if total is not None else 0,
            rows=[Cliente.from_api(row) for row in rows],
        )
