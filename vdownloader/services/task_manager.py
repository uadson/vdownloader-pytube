"""Gerenciador de tarefas assíncronas de download de mídias em segundo plano."""

from dataclasses import dataclass, field
from pathlib import Path
import threading
import time
from typing import Any, Dict, Optional
import uuid

from vdownloader.services.downloader import MediaService


@dataclass
class DownloadJob:
    """Representação em memória de uma tarefa de download assíncrono."""

    task_id: str
    url: str
    media_type: str
    resolution: Optional[str]
    status: str = "pending"
    progress: float = 0.0
    message: Optional[str] = "Tarefa enfileirada..."
    filename: Optional[str] = None
    file_path: Optional[Path] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)


class DownloadTaskManager:
    """Gerencia a criação, execução e ciclo de vida de tarefas de download assíncronas."""

    def __init__(self, media_service: Optional[MediaService] = None) -> None:
        """Inicializa o gerenciador de tarefas.

        Args:
            media_service: Instância opcional de MediaService.
        """
        self.media_service = media_service or MediaService()
        self._jobs: Dict[str, DownloadJob] = {}
        self._lock = threading.Lock()

    def get_job(self, task_id: str) -> Optional[DownloadJob]:
        """Obtém uma tarefa pelo seu identificador único.

        Args:
            task_id: Identificador único da tarefa.

        Returns:
            Optional[DownloadJob]: Instância da tarefa ou None caso não exista.
        """
        with self._lock:
            return self._jobs.get(task_id)

    def _update_job(
        self,
        task_id: str,
        status: Optional[str] = None,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        filename: Optional[str] = None,
        file_path: Optional[Path] = None,
        error: Optional[str] = None,
    ) -> None:
        """Atualiza os campos de uma tarefa de maneira thread-safe."""
        with self._lock:
            job = self._jobs.get(task_id)
            if not job:
                return
            if status is not None:
                job.status = status
            if progress is not None:
                job.progress = progress
            if message is not None:
                job.message = message
            if filename is not None:
                job.filename = filename
            if file_path is not None:
                job.file_path = file_path
            if error is not None:
                job.error = error

    def _progress_hook(self, task_id: str, data: Dict[str, Any]) -> None:
        """Callback acionado periodicamente pelo yt-dlp durante o download.

        Args:
            task_id: ID da tarefa sendo processada.
            data: Dicionário de telemetria emitido pelo yt-dlp.
        """
        hook_status = data.get("status")
        if hook_status == "downloading":
            total_bytes = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            downloaded = data.get("downloaded_bytes") or 0
            if total_bytes > 0:
                pct = round((downloaded / total_bytes) * 100, 1)
                self._update_job(
                    task_id=task_id,
                    status="downloading",
                    progress=pct,
                    message=f"Baixando mídia do YouTube: {pct:.1f}% concluído...",
                )
            else:
                self._update_job(
                    task_id=task_id,
                    status="downloading",
                    message="Baixando fluxo de mídia do YouTube...",
                )
        elif hook_status == "finished":
            self._update_job(
                task_id=task_id,
                status="processing",
                progress=95.0,
                message="Mesclando áudio e vídeo com FFmpeg...",
            )

    def _execute_download(self, task_id: str) -> None:
        """Executa a operação de download em thread separada.

        Args:
            task_id: Identificador da tarefa a ser processada.
        """
        job = self.get_job(task_id)
        if not job:
            return

        self._update_job(
            task_id=task_id,
            status="downloading",
            progress=0.0,
            message="Iniciando download da mídia...",
        )

        try:
            file_path = self.media_service.download_media(
                url=job.url,
                media_type=job.media_type,
                resolution=job.resolution,
                progress_hook=lambda d: self._progress_hook(task_id, d),
            )

            if not file_path.exists():
                raise RuntimeError("Arquivo gerado não foi localizado no disco.")

            self._update_job(
                task_id=task_id,
                status="ready",
                progress=100.0,
                message="Mídia processada e pronta para transferência!",
                filename=file_path.name,
                file_path=file_path,
            )
        except Exception as exc:
            self._update_job(
                task_id=task_id,
                status="failed",
                error=str(exc),
                message=f"Falha ao processar mídia: {str(exc)}",
            )

    def create_job(
        self,
        url: str,
        media_type: str = "video",
        resolution: Optional[str] = "best",
    ) -> str:
        """Cria e inicia uma nova tarefa de download em segundo plano.

        Args:
            url: Endereço do vídeo.
            media_type: 'video' ou 'audio'.
            resolution: Resolução desejada.

        Returns:
            str: Identificador único gerado para a tarefa (task_id).
        """
        self.cleanup_old_jobs()

        task_id = str(uuid.uuid4())
        job = DownloadJob(
            task_id=task_id,
            url=url,
            media_type=media_type,
            resolution=resolution,
        )

        with self._lock:
            self._jobs[task_id] = job

        worker_thread = threading.Thread(
            target=self._execute_download,
            args=(task_id,),
            daemon=True,
        )
        worker_thread.start()

        return task_id

    def cleanup_old_jobs(self, max_age_seconds: int = 3600) -> None:
        """Remove tarefas antigas da memória para evitar vazamento de recursos.

        Args:
            max_age_seconds: Tempo máximo de vida de uma tarefa em segundos.
        """
        now = time.time()
        with self._lock:
            expired_ids = [
                t_id
                for t_id, j in self._jobs.items()
                if now - j.created_at > max_age_seconds
            ]
            for t_id in expired_ids:
                del self._jobs[t_id]
