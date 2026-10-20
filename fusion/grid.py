from __future__ import annotations

import logging

from fusion.exceptions import FusionError
from fusion.http import HttpSession

logger = logging.getLogger("fusion.grid")


def search(
    http: HttpSession,
    path: str,
    campo: str,
    valor: str,
    *,
    page: int,
    rows: int,
    referer_menu: str,
) -> tuple[int, list[dict]]:
    """POST to one of the Fusion portal's get_<entity>.php grid endpoints.

    These share one request/response shape across the portal: filter by any
    single column present in the joined response (not just the ones each
    screen's UI exposes), paginate with page/rows, and get back
    {"total": ..., "rows": [...]} — both come back null instead of 0/[] when
    there's no match.
    """
    logger.debug("Searching %s: %s=%s (page=%s, rows=%s)", path, campo, valor, page, rows)

    response = http.post(
        path,
        params={"LGPD": 0},
        data={"campo": campo, "valor": valor, "page": page, "rows": rows},
        headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{http.config.base_url}/html/menus/main.php?menu={referer_menu}",
        },
    )

    data = response.json()
    if "rows" not in data:
        raise FusionError(f"Unexpected response from {path}: {data}")

    total = data.get("total")
    rows_data = data.get("rows") or []

    return (int(total) if total is not None else 0), rows_data
