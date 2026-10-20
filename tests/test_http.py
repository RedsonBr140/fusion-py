import pytest

from fusion.config import FusionConfig
from fusion.exceptions import FusionHTTPError
from fusion.http import HttpSession


def test_get_raises_fusion_http_error_on_failure(requests_mock):
    http = HttpSession(FusionConfig())
    requests_mock.get(f"{http.config.base_url}/broken", status_code=500)

    with pytest.raises(FusionHTTPError) as exc_info:
        http.get("/broken")

    assert exc_info.value.status_code == 500


def test_timeout_is_applied_by_default(requests_mock):
    http = HttpSession(FusionConfig(timeout=5))
    requests_mock.get(f"{http.config.base_url}/ok", json={})

    http.get("/ok")

    assert requests_mock.last_request.timeout == 5
