from pathlib import Path
import shutil

import requests

from fusion.auth import FusionAuth
from fusion.company import Company


class FusionClient:
    BASE_URL = "https://fusiondms.com.br"

    def __init__(self, download_dir: str):
        self.download_dir = Path.cwd() / download_dir

        if self.download_dir.exists():
            shutil.rmtree(self.download_dir)

        self.download_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update(
            {
                "accept-language": "pt-BR,pt;q=0.9",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/148.0.0.0 Safari/537.36"
                ),
            }
        )

        self.token: str | None = None
        self.company: Company | None = None

        self.auth = FusionAuth(self)

    def _headers(self, extra: dict | None = None) -> dict:
        """Base headers merged with any call-site overrides."""
        headers: dict = {"Accept": "application/json"}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        if extra:
            headers.update(extra)

        return headers

    def get(self, path: str, **kwargs) -> requests.Response:
        response = self.session.get(
            f"{self.BASE_URL}{path}",
            headers=self._headers(kwargs.pop("headers", None)),
            **kwargs,
        )
        response.raise_for_status()
        return response

    def post(self, path: str, **kwargs) -> requests.Response:
        response = self.session.post(
            f"{self.BASE_URL}{path}",
            headers=self._headers(kwargs.pop("headers", None)),
            **kwargs,
        )
        response.raise_for_status()
        return response

    def download(self, path: str, filename: str, **kwargs) -> Path:
        """Stream a file download into self.download_dir."""
        response = self.get(path, stream=True, **kwargs)

        dest = self.download_dir / filename

        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return dest

    def login(self, username: str, password: str):
        self.auth.login(username, password)

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
