from __future__ import annotations

import logging

from fusion.exceptions import FusionAuthError
from fusion.http import HttpSession
from fusion.models import Company, LoginResult

logger = logging.getLogger("fusion.auth")

LOGIN_PAGE_PATH = "/login.html"
LOGIN_PATH = "/php/util/login.php"


class AuthService:
    def __init__(self, http: HttpSession):
        self._http = http

    def login(self, username: str, password: str) -> LoginResult:
        logger.info("Logging in as %s", username)

        # The portal issues fresh AWSALB/AWSALBCORS cookies on the login page;
        # the session carries them automatically into the POST below, and the
        # POST is rejected without them.
        self._http.get(
            LOGIN_PAGE_PATH,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
            },
        )

        response = self._http.post(
            LOGIN_PATH,
            data={
                "user_login": username,
                "user_pass": password,
                "cc_login_modulo": 4,
            },
            headers={
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self._http.config.base_url}{LOGIN_PAGE_PATH}",
            },
        )

        data = response.json()
        if not data.get("success"):
            raise FusionAuthError(f"Login failed: {data}")

        company = Company(
            codigo=data["sis04_codigo"],
            fantasia=data["fantasia"],
            cnpj=data["cnpj"],
        )
        logger.info("Login completed — %s", company.fantasia)

        return LoginResult(token=data["token"], company=company)
