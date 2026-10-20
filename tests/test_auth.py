import pytest

from fusion.client import FusionClient
from fusion.exceptions import FusionAuthError


def test_login_success(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")

    requests_mock.get(f"{client._http.config.base_url}/login.html", text="<html></html>")
    requests_mock.post(
        f"{client._http.config.base_url}/php/util/login.php",
        json={
            "success": True,
            "token": "abc123",
            "sis04_codigo": "1",
            "fantasia": "Acme Motors",
            "cnpj": "00.000.000/0001-00",
        },
    )

    client.login("user", "pass")

    assert client.is_logged_in
    assert client.token == "abc123"
    assert client.company.fantasia == "Acme Motors"


def test_login_failure_raises(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")

    requests_mock.get(f"{client._http.config.base_url}/login.html", text="<html></html>")
    requests_mock.post(
        f"{client._http.config.base_url}/php/util/login.php",
        json={"success": False, "message": "invalid credentials"},
    )

    with pytest.raises(FusionAuthError):
        client.login("user", "wrong-pass")

    assert not client.is_logged_in


def test_login_succeeds_when_cnpj_is_missing(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")

    requests_mock.get(f"{client._http.config.base_url}/login.html", text="<html></html>")
    requests_mock.post(
        f"{client._http.config.base_url}/php/util/login.php",
        json={
            "success": True,
            "token": "abc123",
            "sis04_codigo": "1",
            "fantasia": "Acme Motors",
            # no "cnpj" key — observed on at least one real portal instance
        },
    )

    client.login("user", "pass")

    assert client.is_logged_in
    assert client.token == "abc123"
    assert client.company.cnpj == ""


def test_authorization_header_sent_after_login(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")

    requests_mock.get(f"{client._http.config.base_url}/login.html", text="<html></html>")
    requests_mock.post(
        f"{client._http.config.base_url}/php/util/login.php",
        json={
            "success": True,
            "token": "abc123",
            "sis04_codigo": "1",
            "fantasia": "Acme Motors",
            "cnpj": "00.000.000/0001-00",
        },
    )
    client.login("user", "pass")

    requests_mock.get(f"{client._http.config.base_url}/api/ping", json={"ok": True})
    client.get("/api/ping")

    assert requests_mock.last_request.headers["Authorization"] == "Bearer abc123"
