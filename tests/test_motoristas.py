import pytest

from fusion.client import FusionClient
from fusion.services.motoristas import CAMPO_NOME, GET_MOTORISTAS_PATH

RAW_ROW = {
    "t05_id": "13768",
    "t05_nome": "ALEX MACIEL (SOMENTE PARA CARGAS)",
    "t05_cpf": "12345678900",
    "t05_telefone": ".",
    "t05_endereco": "RUA EXEMPLO",
    "t05_uf": "PE",
    "t05_cidade": "RECIFE",
    "t05_cep": "50000000",
    "t05_latitude": "-8.0476",
    "t05_longitude": "-34.8770",
    "t05_codigo_erp": "52649",
    "t05_status": "Escalado",
    "t05_tipo": "Motorista",
    "t05_email": "",
}


def test_buscar_motoristas_parses_rows(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")
    url = f"{client._http.config.base_url}{GET_MOTORISTAS_PATH}"
    requests_mock.post(url, json={"total": "1", "rows": [RAW_ROW]})

    page = client.buscar_motoristas(CAMPO_NOME, "alex")

    assert page.total == 1
    motorista = page.rows[0]
    assert motorista.nome == "ALEX MACIEL (SOMENTE PARA CARGAS)"
    assert motorista.codigo_erp == "52649"
    assert motorista.latitude == pytest.approx(-8.0476)
    assert motorista.status == "Escalado"
    assert motorista.email is None


def test_buscar_motoristas_handles_no_match(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")
    url = f"{client._http.config.base_url}{GET_MOTORISTAS_PATH}"
    requests_mock.post(url, json={"total": None, "rows": None})

    page = client.buscar_motoristas(CAMPO_NOME, "does-not-exist")

    assert page.total == 0
    assert page.rows == []


def test_buscar_motoristas_sends_filter(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")
    url = f"{client._http.config.base_url}{GET_MOTORISTAS_PATH}"
    requests_mock.post(url, json={"total": "0", "rows": []})

    client.buscar_motoristas(CAMPO_NOME, "alex", page=1, rows=10)

    sent = requests_mock.last_request
    assert sent.text == f"campo={CAMPO_NOME}&valor=alex&page=1&rows=10"
