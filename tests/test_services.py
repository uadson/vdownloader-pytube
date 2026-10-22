"""Testes unitários e de integração para os serviços de download e extração."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from vdownloader.services.downloader import MediaService


def test_format_duration_seconds() -> None:
    """Valida a formatação de segundos para MM:SS."""
    service = MediaService()
    assert service.format_duration(65) == "01:05"
    assert service.format_duration(0) == "00:00"


def test_format_duration_hours() -> None:
    """Valida a formatação de duração contendo horas para HH:MM:SS."""
    service = MediaService()
    assert service.format_duration(3665) == "01:01:05"


def test_format_duration_none() -> None:
    """Valida que duração nula retorne string zerada."""
    service = MediaService()
    assert service.format_duration(None) == "00:00"


@patch("yt_dlp.YoutubeDL")
def test_extract_info_success(mock_ydl_class: MagicMock) -> None:
    """Valida extração de metadados com sucesso a partir de URL do YouTube.

    Args:
        mock_ydl_class: Mock da classe YoutubeDL do yt-dlp.
    """
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = {
        "title": "Vídeo de Teste",
        "uploader": "Canal Exemplo",
        "duration": 180,
        "thumbnail": "https://i.ytimg.com/vi/test/hqdefault.jpg",
        "description": "Descrição detalhada do vídeo de teste.",
        "webpage_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    }
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    service = MediaService()
    info = service.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    assert info["title"] == "Vídeo de Teste"
    assert info["author"] == "Canal Exemplo"
    assert info["duration"] == 180
    assert info["duration_formatted"] == "03:00"
    assert len(info["options"]) > 0


@patch("yt_dlp.YoutubeDL")
def test_extract_info_invalid_url(mock_ydl_class: MagicMock) -> None:
    """Valida que uma URL inválida lance exceção apropriada.

    Args:
        mock_ydl_class: Mock da classe YoutubeDL do yt-dlp.
    """
    mock_instance = MagicMock()
    mock_instance.extract_info.side_effect = Exception("URL não suportada ou inexistente")
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    service = MediaService()
    with pytest.raises(ValueError) as excinfo:
        service.extract_info("https://link-invalido.com")

    assert "Falha ao extrair informações do vídeo" in str(excinfo.value)
