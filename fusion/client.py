from __future__ import annotations

from pathlib import Path

import requests

from fusion.config import FusionConfig
from fusion.http import HttpSession
from fusion.models import ClientesPage, Company
from fusion.services.auth import AuthService
from fusion.services.clientes import ClientesService


class FusionClient:
    def __init__(self, download_dir: str | Path, *, config: FusionConfig | None = None):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        self._http = HttpSession(config or FusionConfig())
        self._auth = AuthService(self._http)
        self._clientes = ClientesService(self._http)

        self.company: Company | None = None

    @property
    def token(self) -> str | None:
        return self._http.token

    @property
    def is_logged_in(self) -> bool:
        return self.token is not None

    def login(self, username: str, password: str) -> None:
        result = self._auth.login(username, password)
        self._http.token = result.token
        self.company = result.company

    def buscar_clientes(
        self, campo: str, valor: str, *, page: int = 1, rows: int = 10
    ) -> ClientesPage:
        return self._clientes.buscar(campo, valor, page=page, rows=rows)

    def get(self, path: str, **kwargs) -> requests.Response:
        return self._http.get(path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self._http.post(path, **kwargs)

    def download(self, path: str, filename: str, **kwargs) -> Path:
        """Stream a file download into self.download_dir."""
        response = self.get(path, stream=True, **kwargs)
        dest = self.download_dir / filename

        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return dest

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> FusionClient:
        return self

    def __exit__(self, *_exc) -> None:
        self.close()
