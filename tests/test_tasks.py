"""Testes unitários e de integração para o gerenciador de tarefas de download assíncrono."""

from pathlib import Path
import time
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest

from vdownloader.api.app import app
from vdownloader.services.task_manager import DownloadJob, DownloadTaskManager


@pytest.fixture
def client() -> TestClient:
    """Fixture que fornece um cliente de testes da API FastAPI.

    Returns:
        TestClient: Instância do TestClient configurada.
    """
    return TestClient(app)


def test_task_manager_create_and_get_job(tmp_path: Path) -> None:
    """Valida a criação e recuperação de uma tarefa de download."""
    manager = DownloadTaskManager()
    task_id = manager.create_job(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        media_type="video",
        resolution="720p",
    )

    job = manager.get_job(task_id)
    assert job is not None
    assert job.task_id == task_id
    assert job.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert job.status in ("pending", "downloading")


def test_task_manager_success_execution(tmp_path: Path) -> None:
    """Valida o ciclo de vida completo de uma tarefa concluída com sucesso."""
    fake_file = tmp_path / "meu_video.mp4"
    fake_file.write_bytes(b"dados do video")

    mock_service = MagicMock()
    mock_service.download_media.return_value = fake_file

    manager = DownloadTaskManager(media_service=mock_service)
    task_id = manager.create_job(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        media_type="video",
        resolution="720p",
    )

    # Aguarda a thread de processamento finalizar
    max_wait = 2.0
    start = time.time()
    while time.time() - start < max_wait:
        job = manager.get_job(task_id)
        if job and job.status == "ready":
            break
        time.sleep(0.05)

    job = manager.get_job(task_id)
    assert job is not None
    assert job.status == "ready"
    assert job.progress == 100.0
    assert job.file_path == fake_file
    assert job.filename == "meu_video.mp4"


def test_task_manager_failure_execution() -> None:
    """Valida o tratamento de falha durante a execução de uma tarefa."""
    mock_service = MagicMock()
    mock_service.download_media.side_effect = RuntimeError("Erro simulado no yt-dlp")

    manager = DownloadTaskManager(media_service=mock_service)
    task_id = manager.create_job(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        media_type="video",
        resolution="720p",
    )

    max_wait = 2.0
    start = time.time()
    while time.time() - start < max_wait:
        job = manager.get_job(task_id)
        if job and job.status == "failed":
            break
        time.sleep(0.05)

    job = manager.get_job(task_id)
    assert job is not None
    assert job.status == "failed"
    assert "Erro simulado no yt-dlp" in (job.error or "")


def test_api_start_task_endpoint(client: TestClient) -> None:
    """Valida o endpoint POST /api/download/start."""
    response = client.post(
        "/api/download/start",
        json={
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "media_type": "video",
            "resolution": "720p",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] in ("pending", "downloading")


def test_api_task_status_lifecycle(client: TestClient, tmp_path: Path) -> None:
    """Valida a consulta de status e download do arquivo via API."""
    fake_file = tmp_path / "video_pronto.mp4"
    fake_file.write_bytes(b"conteudo final em mp4")

    with patch("vdownloader.api.app.task_manager.media_service.download_media") as mock_dl:
        mock_dl.return_value = fake_file

        # 1. Inicia a tarefa
        start_resp = client.post(
            "/api/download/start",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "media_type": "video",
                "resolution": "720p",
            },
        )
        assert start_resp.status_code == 200
        task_id = start_resp.json()["task_id"]

        # 2. Faz polling do status até estar pronto
        max_wait = 2.0
        start_time = time.time()
        ready = False
        while time.time() - start_time < max_wait:
            status_resp = client.get(f"/api/download/task/{task_id}")
            assert status_resp.status_code == 200
            data = status_resp.json()
            if data["status"] == "ready":
                ready = True
                break
            time.sleep(0.05)

        assert ready is True

        # 3. Baixa o arquivo pronto
        file_resp = client.get(f"/api/download/file/{task_id}")
        assert file_resp.status_code == 200
        assert file_resp.content == b"conteudo final em mp4"
        assert "video_pronto.mp4" in file_resp.headers.get("content-disposition", "")


def test_api_task_not_found(client: TestClient) -> None:
    """Valida erro 404 para ID de tarefa inexistente."""
    response = client.get("/api/download/task/tarefa-inexistente-123")
    assert response.status_code == 404

    file_response = client.get("/api/download/file/tarefa-inexistente-123")
    assert file_response.status_code == 404
