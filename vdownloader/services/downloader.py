"""Serviço responsável pela extração de metadados e download de mídias."""

from pathlib import Path
import os
import re
import shutil
import tempfile
from typing import Any, Callable, Dict, List, Optional
import yt_dlp


class MediaService:
    """Serviço que orquestra a obtenção de metadados e download de vídeos e áudios."""

    def __init__(self, download_dir: Optional[Path] = None) -> None:
        """Inicializa o serviço de mídia.

        Args:
            download_dir: Diretório onde os arquivos temporários serão gravados.
                Caso omitido, utiliza uma pasta temporária padrão.
        """
        if download_dir:
            self.download_dir = Path(download_dir)
        else:
            self.download_dir = Path(tempfile.gettempdir()) / "vdownloader_media"
        self.download_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitiza o nome do arquivo para compatibilidade com sistemas de arquivos e HTTP.

        Args:
            name: Nome original do arquivo ou título do vídeo.

        Returns:
            str: Nome sanitizado livre de caracteres reservados e quebras de codificação.
        """
        # Substitui caracteres reservados de sistemas de arquivos e unicode problemático como \uff5c
        sanitized = re.sub(r'[\\/*?:"<>|\uff5c]', "_", name)
        # Remove espaços repetidos e caracteres de controle
        sanitized = re.sub(r'\s+', " ", sanitized).strip()
        return sanitized or "download"

    def format_duration(self, seconds: Optional[int | float]) -> str:
        """Formata o tempo em segundos para representação em string.

        Args:
            seconds: Duração total em segundos.

        Returns:
            str: Tempo formatado no padrão HH:MM:SS ou MM:SS.
        """
        if not seconds or seconds <= 0:
            return "00:00"

        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def format_speed(bytes_per_sec: Optional[float | int]) -> str:
        """Formata velocidade de transferência em bytes por segundo para representação legível.

        Args:
            bytes_per_sec: Taxa de download em bytes por segundo.

        Returns:
            str: Velocidade formatada em MB/s ou KB/s.
        """
        if not bytes_per_sec or bytes_per_sec <= 0:
            return ""

        speed_val = float(bytes_per_sec)
        if speed_val >= 1024 * 1024:
            return f"{speed_val / (1024 * 1024):.1f} MB/s"
        return f"{speed_val / 1024:.1f} KB/s"

    @staticmethod
    def format_eta(seconds: Optional[float | int]) -> str:
        """Formata o tempo restante estimado (ETA) em segundos.

        Args:
            seconds: Segundos restantes estimados.

        Returns:
            str: Tempo restante amigável (ex: '45s', '02:30', '01:15:20').
        """
        if not seconds or seconds <= 0:
            return ""

        total_secs = int(seconds)
        if total_secs < 60:
            return f"{total_secs}s"

        hours = total_secs // 3600
        mins = (total_secs % 3600) // 60
        secs = total_secs % 60

        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"

    def extract_info(self, url: str) -> Dict[str, Any]:
        """Extrai metadados completos de um vídeo a partir da sua URL.

        Args:
            url: Endereço web do vídeo no YouTube ou plataforma suportada.

        Returns:
            Dict[str, Any]: Dicionário com título, autor, duração, thumbnail,
                descrição e lista de opções de download disponíveis.

        Raises:
            ValueError: Quando a URL for inválida ou não puder ser extraída.
        """
        ydl_opts: Dict[str, Any] = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": False,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise ValueError("Nenhum dado retornado para a URL informada.")

                duration = info.get("duration")
                options: List[Dict[str, Any]] = [
                    {
                        "format_id": "video_hq",
                        "label": "Vídeo Melhor Qualidade (HQ)",
                        "media_type": "video",
                        "resolution": "best",
                        "ext": "mp4",
                        "is_audio": False,
                    },
                    {
                        "format_id": "video_1080p",
                        "label": "Vídeo 1080p (Full HD)",
                        "media_type": "video",
                        "resolution": "1080p",
                        "ext": "mp4",
                        "is_audio": False,
                    },
                    {
                        "format_id": "video_720p",
                        "label": "Vídeo 720p (HD)",
                        "media_type": "video",
                        "resolution": "720p",
                        "ext": "mp4",
                        "is_audio": False,
                    },
                    {
                        "format_id": "video_360p",
                        "label": "Vídeo 360p (Econômico)",
                        "media_type": "video",
                        "resolution": "360p",
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
                ]

                return {
                    "id": info.get("id", ""),
                    "title": info.get("title", "Sem título"),
                    "author": info.get("uploader", "Desconhecido"),
                    "duration": duration or 0,
                    "duration_formatted": self.format_duration(duration),
                    "thumbnail": info.get("thumbnail", ""),
                    "description": info.get("description", "") or "",
                    "url": info.get("webpage_url", url),
                    "options": options,
                }
        except Exception as exc:
            raise ValueError(f"Falha ao extrair informações do vídeo: {str(exc)}") from exc

    def download_media(
        self,
        url: str,
        media_type: str = "video",
        resolution: Optional[str] = "best",
        progress_hook: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Path:
        """Executa o download da mídia solicitada e retorna o caminho do arquivo gerado.

        Args:
            url: Endereço do vídeo.
            media_type: Tipo de mídia desejada ('video' ou 'audio').
            resolution: Resolução desejada ('360p', '720p', '1080p', 'best').
            progress_hook: Função opcional de callback chamada durante o progresso do download.

        Returns:
            Path: Caminho absoluto para o arquivo de mídia baixado.

        Raises:
            RuntimeError: Quando ocorrer erro durante o processamento do download.
        """
        output_template = str(self.download_dir / "%(title).150B-%(id)s.%(ext)s")
        has_ffmpeg = shutil.which("ffmpeg") is not None

        common_opts: Dict[str, Any] = {
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "concurrent_fragment_downloads": 5,
            "buffersize": 1024 * 64,
            "http_chunk_size": 10485760,
            "retries": 10,
            "fragment_retries": 10,
        }

        if media_type == "audio":
            ydl_opts: Dict[str, Any] = {
                **common_opts,
                "format": "bestaudio/best",
            }
            # Se o ffmpeg estiver instalado, converte para mp3. Caso contrário, mantém o áudio nativo.
            if has_ffmpeg:
                ydl_opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ]
        else:
            format_selector = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            if resolution == "1080p":
                format_selector = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best"
            elif resolution == "720p":
                format_selector = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best"
            elif resolution == "360p":
                format_selector = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best"

            ydl_opts = {
                **common_opts,
                "format": format_selector,
            }
            if has_ffmpeg:
                ydl_opts["merge_output_format"] = "mp4"

        if progress_hook:
            ydl_opts["progress_hooks"] = [progress_hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = Path(ydl.prepare_filename(info))

                # Caso tenha sido pós-processado para mp3
                if media_type == "audio" and has_ffmpeg:
                    possible_mp3 = downloaded_file.with_suffix(".mp3")
                    if possible_mp3.exists():
                        return possible_mp3

                if downloaded_file.exists():
                    return downloaded_file

                # Busca pelo arquivo mais recente na pasta caso a extensão tenha mudado
                target_stem = downloaded_file.stem
                for candidate in self.download_dir.iterdir():
                    if candidate.stem.startswith(target_stem[:40]):
                        return candidate

                raise RuntimeError("Arquivo baixado não foi localizado no disco.")
        except Exception as exc:
            raise RuntimeError(f"Erro ao baixar a mídia: {str(exc)}") from exc
