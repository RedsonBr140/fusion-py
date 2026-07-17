from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fusion.client import FusionClient

from fusion.company import Company
from fusion.exceptions import FusionAuthError


class FusionAuth:
    LOGIN_PAGE_URL = "/login.html"
    LOGIN_URL = "/php/util/login.php"

    def __init__(self, client: FusionClient):
        self.client = client

    def is_logged_in(self) -> bool:
        return self.client.token is not None

    def login(self, username: str, password: str):
        print("Logging in...")

        # Step 1: GET login page — populates AWSALB/AWSALBCORS into the session
        self.client.get(
            self.LOGIN_PAGE_URL,
            headers={
                "accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "*/*;q=0.8"
                ),
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
            },
        )

        # Step 2: POST credentials — session carries the fresh AWS cookies automatically
        response = self.client.post(
            self.LOGIN_URL,
            data={
                "user_login": username,
                "user_pass": password,
                "cc_login_modulo": 4,
            },
            headers={
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-requested-with": "XMLHttpRequest",
                "Referer": f"{self.client.BASE_URL}{self.LOGIN_PAGE_URL}",
            },
        )

        data = response.json()

        if not data.get("success"):
            raise FusionAuthError(f"Login failed: {data}")

        self.client.token = data["token"]
        self.client.company = Company(
            codigo=data["sis04_codigo"],
            fantasia=data["fantasia"],
            cnpj=data["cnpj"],
        )

        print(f"Login completed — {self.client.company.fantasia}")
