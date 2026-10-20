import pytest

from fusion.client import FusionClient
from fusion.exceptions import FusionError
from fusion.services.clientes import CAMPO_CODIGO_ERP, GET_CLIENTES_PATH

RAW_ROW = {
    "t16_id": "2938743",
    "t16_fantasia": "",
    "t16_razSocial": "ACME LTDA",
    "t16_cnpjCliente": "12345678000199",
    "t16_endereco": "RUA EXEMPLO",
    "t16_numero_endereco": "203",
    "t16_bairro": "CENTRO",
    "t16_cidade": "RECIFE",
    "t16_uf": "PE",
    "t16_cep": "50000000",
    "t16_celular": "81999999999",
    "t16_email1": "",
    "t44_codigo_erp": "73967",
    "t44_latitude": "-8.0476",
    "t44_longitude": "-34.8770",
    "t44_sn_cliente_ativo": "S",
    "t62_descricao": "Segmento Padrao",
}


def test_buscar_clientes_parses_rows(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")
    url = f"{client._http.config.base_url}{GET_CLIENTES_PATH}"
    requests_mock.post(url, json={"total": "1", "rows": [RAW_ROW]})

    page = client.buscar_clientes(CAMPO_CODIGO_ERP, "73967")

    assert page.total == 1
    assert len(page.rows) == 1

    cliente = page.rows[0]
    assert cliente.codigo_erp == "73967"
    assert cliente.cnpj == "12345678000199"
    assert cliente.razao_social == "ACME LTDA"
    assert cliente.latitude == pytest.approx(-8.0476)
    assert cliente.ativo is True
    assert cliente.fantasia is None
    assert cliente.email is None


def test_buscar_clientes_sends_filter_and_pagination(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")
    url = f"{client._http.config.base_url}{GET_CLIENTES_PATH}"
    requests_mock.post(url, json={"total": "0", "rows": []})

    client.buscar_clientes(CAMPO_CODIGO_ERP, "73967", page=2, rows=25)

    sent = requests_mock.last_request
    assert sent.qs["lgpd"] == ["0"]
    assert sent.text == f"campo={CAMPO_CODIGO_ERP}&valor=73967&page=2&rows=25"


def test_buscar_clientes_raises_on_unexpected_response(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")
    url = f"{client._http.config.base_url}{GET_CLIENTES_PATH}"
    requests_mock.post(url, json={"error": "session expired"})

    with pytest.raises(FusionError):
        client.buscar_clientes(CAMPO_CODIGO_ERP, "73967")
