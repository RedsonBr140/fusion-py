from fusion.client import FusionClient


def test_download_dir_is_created_but_not_wiped(tmp_path):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    keep = download_dir / "keep.txt"
    keep.write_text("do not delete me")

    client = FusionClient(download_dir)

    assert keep.exists()
    assert keep.read_text() == "do not delete me"
    client.close()


def test_download_streams_to_file(requests_mock, tmp_path):
    client = FusionClient(tmp_path / "downloads")
    requests_mock.get(
        f"{client._http.config.base_url}/files/report.pdf",
        content=b"pdf-bytes",
    )

    dest = client.download("/files/report.pdf", "report.pdf")

    assert dest.read_bytes() == b"pdf-bytes"
    client.close()


def test_context_manager_closes_session(tmp_path):
    with FusionClient(tmp_path / "downloads") as client:
        assert client._http is not None
