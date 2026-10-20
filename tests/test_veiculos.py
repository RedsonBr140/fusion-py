import pytest

from fusion.client import FusionClient
from fusion.services.veiculos import GET_TRANSPORTES_PATH

RAW_ROW = {
    "t06_id": "10887",
    "t06_descricao": "FIAT/STRADA ENDURAN CS 1.3",
    "t06_placa": "UHM-6C71",
    "t06_codigo_erp": "52",
    "t06_status": "Livre",
    "t06_modelo": "Strada Enduran CS 1.3",
    "t06_anoModelo": "2026",
    "t06_anoFabricacao": "2025",
    "t06_kmAtual": "36905",
    "t06_tipo_combustivel": "Diesel",
    "t06_sn_proprio": "S",
    "t06_latitudeAtual": "-7.8331543",
    "t06_longitudeAtual": "-38.1043058",
    "t05_id": "13804",
    "t05_nome": "GEYDSON (SOMENTE PARA ENTREGAS)",
    # t96_* (tipo de veiculo) columns intentionally omitted — out of scope.
    "t96_id": "138",
    "t96_descricao": "UTILITARIO",
}


def test_buscar_veiculos_parses_rows(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")
    url = f"{client._http.config.base_url}{GET_TRANSPORTES_PATH}"
    requests_mock.post(url, json={"total": "1", "rows": [RAW_ROW]})

    page = client.buscar_veiculos()

    assert page.total == 1
    veiculo = page.rows[0]
    assert veiculo.placa == "UHM-6C71"
    assert veiculo.codigo_erp == "52"
    assert veiculo.km_atual == 36905
    assert veiculo.proprio is True
    assert veiculo.latitude == pytest.approx(-7.8331543)
    assert veiculo.motorista_nome == "GEYDSON (SOMENTE PARA ENTREGAS)"


def test_buscar_veiculos_handles_no_match(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")
    url = f"{client._http.config.base_url}{GET_TRANSPORTES_PATH}"
    requests_mock.post(url, json={"total": None, "rows": None})

    page = client.buscar_veiculos(page=1, rows=250)

    assert page.total == 0
    assert page.rows == []


def test_buscar_veiculos_sends_no_lgpd_param(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")
    url = f"{client._http.config.base_url}{GET_TRANSPORTES_PATH}"
    requests_mock.post(url, json={"total": "0", "rows": []})

    client.buscar_veiculos(page=1, rows=250)

    sent = requests_mock.last_request
    assert "lgpd" not in sent.qs
    assert sent.text == "campo=&valor=&page=1&rows=250"
