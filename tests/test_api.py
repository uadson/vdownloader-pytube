"""Testes de integração para os endpoints da API FastAPI."""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest

from vdownloader.api.app import app


@pytest.fixture
def client() -> TestClient:
    """Fixture que fornece um cliente de testes da API FastAPI.

    Returns:
        TestClient: Instância do TestClient configurada.
    """
    return TestClient(app)


def test_health_endpoint(client: TestClient) -> None:
    """Valida o endpoint de health check."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@patch("vdownloader.services.downloader.MediaService.extract_info")
def test_info_endpoint_success(mock_extract: MagicMock, client: TestClient) -> None:
    """Valida o endpoint POST /api/info quando os dados são válidos.

    Args:
        mock_extract: Mock do método extract_info do MediaService.
        client: Cliente de teste HTTP.
    """
    mock_extract.return_value = {
        "title": "Clipe de Música Legal",
        "author": "Banda Teste",
        "duration": 240,
        "duration_formatted": "04:00",
        "thumbnail": "https://i.ytimg.com/vi/test/hqdefault.jpg",
        "description": "Clipe musical em alta resolução.",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "options": [
            {
                "format_id": "video_1080p",
                "label": "Vídeo 1080p (Full HD)",
                "media_type": "video",
                "resolution": "1080p",
                "ext": "mp4",
                "is_audio": False,
            },
            {
                "format_id": "audio_mp3",
                "label": "Áudio MP3 (Melhor Qualidade)",
                "media_type": "audio",
                "resolution": None,
                "ext": "mp3",
                "is_audio": True,
            },
        ],
    }

    response = client.post(
        "/api/info",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Clipe de Música Legal"
    assert data["author"] == "Banda Teste"
    assert len(data["options"]) == 2


def test_info_endpoint_empty_url(client: TestClient) -> None:
    """Valida rejeição de requisição com URL vazia."""
    response = client.post("/api/info", json={"url": "   "})
    assert response.status_code == 422


@patch("vdownloader.services.downloader.MediaService.extract_info")
def test_info_endpoint_extraction_failure(
    mock_extract: MagicMock, client: TestClient
) -> None:
    """Valida erro 400 ao falhar a extração de dados do YouTube."""
    mock_extract.side_effect = ValueError("Falha ao extrair informações do vídeo")
    response = client.post(
        "/api/info",
        json={"url": "https://www.youtube.com/watch?v=invalid"},
    )
    assert response.status_code == 400
    assert "Falha ao extrair informações do vídeo" in response.json()["detail"]


@patch("vdownloader.services.downloader.MediaService.download_media")
def test_download_endpoint_success(
    mock_download: MagicMock, client: TestClient, tmp_path: pytest.TempPathFactory
) -> None:
    """Valida o endpoint GET /api/download com streaming do arquivo.

    Args:
        mock_download: Mock do método download_media do MediaService.
        client: Cliente de teste HTTP.
        tmp_path: Diretório temporário fornecido pelo pytest.
    """
    fake_file = tmp_path / "video_teste.mp4"
    fake_file.write_bytes(b"conteudo binario de video simulado")
    mock_download.return_value = fake_file

    response = client.get(
        "/api/download",
        params={
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "media_type": "video",
            "resolution": "720p",
        },
    )
    assert response.status_code == 200
    assert response.content == b"conteudo binario de video simulado"
    assert "video_teste.mp4" in response.headers.get("content-disposition", "")

