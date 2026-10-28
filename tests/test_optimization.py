"""Testes unitários para otimização de download e telemetria de progresso."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from vdownloader.services.downloader import MediaService
from vdownloader.services.task_manager import DownloadTaskManager


def test_format_speed() -> None:
    """Valida a formatação de velocidade em bytes/segundo para strings amigáveis."""
    service = MediaService()
    assert service.format_speed(None) == ""
    assert service.format_speed(0) == ""
    assert service.format_speed(500 * 1024) == "500.0 KB/s"
    assert service.format_speed(5 * 1024 * 1024) == "5.0 MB/s"


def test_format_eta() -> None:
    """Valida a formatação de tempo restante estimado (ETA)."""
    service = MediaService()
    assert service.format_eta(None) == ""
    assert service.format_eta(45) == "45s"
    assert service.format_eta(125) == "02:05"
    assert service.format_eta(3665) == "01:01:05"


def test_progress_hook_hls_fragments() -> None:
    """Valida o cálculo de progresso em transmissões fragmentadas HLS/DASH."""
    manager = DownloadTaskManager()
    task_id = "test-task-123"

    # Cria tarefa simulada
    manager._jobs[task_id] = MagicMock(
        task_id=task_id,
        status="pending",
        progress=0.0,
        message="",
    )

    # Simula hook emitido pelo yt-dlp para streaming fragmentado sem total_bytes
    hook_data = {
        "status": "downloading",
        "fragment_index": 50,
        "fragment_count": 100,
        "total_bytes": None,
        "downloaded_bytes": 5000000,
        "speed": 2 * 1024 * 1024,
        "eta": 25,
    }

    manager._progress_hook(task_id, hook_data)
    job = manager.get_job(task_id)

    assert job.status == "downloading"
    assert job.progress == 50.0
    assert "50.0%" in job.message
    assert "MB/s" in job.message


@patch("yt_dlp.YoutubeDL")
def test_download_media_concurrent_fragments_option(mock_ydl_class: MagicMock, tmp_path: Path) -> None:
    """Valida se a opção de aceleração concorrente de fragmentos é passada ao yt-dlp."""
    mock_instance = MagicMock()
    fake_file = tmp_path / "video_teste.mp4"
    fake_file.write_bytes(b"dados")
    mock_instance.prepare_filename.return_value = str(fake_file)
    mock_instance.extract_info.return_value = {"id": "test", "title": "video_teste"}
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    service = MediaService(download_dir=tmp_path)
    service.download_media("https://www.youtube.com/watch?v=dQw4w9WgXcQ", media_type="video")

    # Verifica os parâmetros passados para YoutubeDL
    args, kwargs = mock_ydl_class.call_args
    ydl_opts = args[0] if args else kwargs.get("params", {})
    assert ydl_opts.get("concurrent_fragment_downloads") == 5
    assert ydl_opts.get("buffersize") == 1024 * 64
