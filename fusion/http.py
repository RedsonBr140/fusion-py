from __future__ import annotations

import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from fusion.config import FusionConfig
from fusion.exceptions import FusionHTTPError

logger = logging.getLogger("fusion.http")


class HttpSession:
    """Thin wrapper around requests.Session: base URL, auth header, timeout, retries."""

    def __init__(self, config: FusionConfig):
        self.config = config
        self.token: str | None = None

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "Accept-Language": "pt-BR,pt;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "User-Agent": config.user_agent,
            }
        )

        retry = Retry(
            total=config.max_retries,
            backoff_factor=0.5,
            status_forcelist=(502, 503, 504),
            allowed_methods=("GET", "POST"),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def _url(self, path: str) -> str:
        return f"{self.config.base_url}{path}"

    def _headers(self, extra: dict[str, str] | None) -> dict[str, str]:
        headers: dict[str, str] = {}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        if extra:
            headers.update(extra)

        return headers

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        headers = self._headers(kwargs.pop("headers", None))
        timeout = kwargs.pop("timeout", self.config.timeout)

        logger.debug("%s %s", method, path)
        response = self._session.request(
            method, self._url(path), headers=headers, timeout=timeout, **kwargs
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise FusionHTTPError(
                f"{method} {path} failed with status {response.status_code}",
                status_code=response.status_code,
                response=response,
            ) from exc

        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def close(self) -> None:
        self._session.close()
