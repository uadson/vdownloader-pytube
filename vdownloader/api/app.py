"""Aplicação FastAPI para extração e download de mídias do YouTube."""

from pathlib import Path
import re
from typing import Optional
from urllib.parse import quote
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from vdownloader.api.schemas import (
    DownloadJobRequest,
    DownloadJobStatus,
    HealthResponse,
    VideoInfoRequest,
    VideoInfoResponse,
)
from vdownloader.services.downloader import MediaService
from vdownloader.services.task_manager import DownloadTaskManager

VERSION = "0.2.5"

app = FastAPI(
    title="vDownloader API",
    description="API para extração e download de vídeos e áudios do YouTube.",
    version=VERSION,
)

# Habilita CORS para permitir comunicação com o frontend React Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length"],
)

media_service = MediaService()
task_manager = DownloadTaskManager(media_service=media_service)


def cleanup_file(path: Path) -> None:
    """Remove arquivo temporário do disco após o envio ao usuário.

    Args:
        path: Caminho do arquivo a ser excluído.
    """
    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass


@app.get("/api/health", response_model=HealthResponse, tags=["Monitoramento"])
async def health_check() -> HealthResponse:
    """Retorna o status de saúde e versão do serviço.

    Returns:
        HealthResponse: Objeto com status operacional e versão.
    """
    return HealthResponse(status="ok", version=VERSION)


@app.post(
    "/api/info",
    response_model=VideoInfoResponse,
    status_code=status.HTTP_200_OK,
    tags=["Mídia"],
)
def get_video_info(request: VideoInfoRequest) -> VideoInfoResponse:
    """Extrai informações e opções de download de um vídeo do YouTube.

    Args:
        request: Objeto contendo a URL do vídeo.

    Returns:
        VideoInfoResponse: Metadados estruturados e formatos disponíveis.

    Raises:
        HTTPException: Caso a extração falhe devido a link inválido ou restrito.
    """
    url = request.url.strip()
    if not url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A URL informada não pode estar em branco.",
        )

    try:
        data = media_service.extract_info(url)
        return VideoInfoResponse(**data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@app.get("/api/download", tags=["Mídia"])
def download_media(
    background_tasks: BackgroundTasks,
    url: str = Query(..., description="URL do vídeo a ser baixado"),
    media_type: str = Query("video", pattern="^(video|audio)$", description="Tipo de mídia ('video' ou 'audio')"),
    resolution: Optional[str] = Query("best", description="Resolução do vídeo ('360p', '720p', '1080p', 'best')"),
) -> FileResponse:
    """Baixa o vídeo ou áudio do YouTube e o entrega diretamente como anexo.

    Args:
        background_tasks: Gerenciador de tarefas assíncronas do FastAPI.
        url: Endereço do vídeo.
        media_type: 'video' para arquivo MP4 ou 'audio' para MP3.
        resolution: Qualidade desejada do vídeo.

    Returns:
        FileResponse: Arquivo transferido via streaming com cabeçalho de anexo.

    Raises:
        HTTPException: Caso ocorra erro durante o download ou conversão.
    """
    try:
        file_path = media_service.download_media(
            url=url,
            media_type=media_type,
            resolution=resolution,
        )
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="O arquivo requisitado não pôde ser gerado no servidor.",
            )

        # Adiciona tarefa em background para limpeza do arquivo após o streaming
        background_tasks.add_task(cleanup_file, file_path)

        media_mime = "audio/mpeg" if media_type == "audio" else "video/mp4"

        # Sanitiza e formata o cabeçalho Content-Disposition conforme a RFC 5987 / RFC 6266
        # Garante fallback ASCII seguro para cabeçalhos HTTP (latin-1) e nome UTF-8 estendido
        safe_filename = media_service.sanitize_filename(file_path.name)
        ascii_fallback = re.sub(r"[^\x20-\x7E]", "_", safe_filename)
        encoded_filename = quote(safe_filename)
        content_disposition = (
            f'attachment; filename="{ascii_fallback}"; filename*=UTF-8\'\'{encoded_filename}'
        )

        return FileResponse(
            path=str(file_path),
            filename=ascii_fallback,
            media_type=media_mime,
            headers={
                "Content-Disposition": content_disposition,
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao realizar download da mídia: {str(exc)}",
        ) from exc


@app.post(
    "/api/download/start",
    response_model=DownloadJobStatus,
    status_code=status.HTTP_200_OK,
    tags=["Mídia Assíncrona"],
)
def start_download_job(request: DownloadJobRequest) -> DownloadJobStatus:
    """Inicia uma tarefa assíncrona de download e mesclagem de mídia em background.

    Args:
        request: Parâmetros de URL, tipo de mídia e resolução.

    Returns:
        DownloadJobStatus: Objeto de estado com o identificador único da tarefa.
    """
    task_id = task_manager.create_job(
        url=request.url,
        media_type=request.media_type,
        resolution=request.resolution,
    )
    job = task_manager.get_job(task_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível registrar a tarefa de download.",
        )

    return DownloadJobStatus(
        task_id=job.task_id,
        status=job.status,
        progress=job.progress,
        message=job.message,
        filename=job.filename,
        error=job.error,
    )


@app.get(
    "/api/download/task/{task_id}",
    response_model=DownloadJobStatus,
    tags=["Mídia Assíncrona"],
)
def get_download_task_status(task_id: str) -> DownloadJobStatus:
    """Consulta o status atual e progresso de uma tarefa de download.

    Args:
        task_id: Identificador único retornado na inicialização da tarefa.

    Returns:
        DownloadJobStatus: Detalhes do estado atual, progresso e mensagens.

    Raises:
        HTTPException: Caso a tarefa não exista ou já tenha expirado.
    """
    job = task_manager.get_job(task_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarefa '{task_id}' não encontrada ou expirada.",
        )

    return DownloadJobStatus(
        task_id=job.task_id,
        status=job.status,
        progress=job.progress,
        message=job.message,
        filename=job.filename,
        error=job.error,
    )


@app.get("/api/download/file/{task_id}", tags=["Mídia Assíncrona"])
def get_download_task_file(
    task_id: str,
    background_tasks: BackgroundTasks,
) -> FileResponse:
    """Transfere o arquivo gerado por uma tarefa concluída diretamente como anexo.

    Args:
        task_id: Identificador único da tarefa de download.
        background_tasks: Gerenciador de tarefas em background do FastAPI.

    Returns:
        FileResponse: Arquivo em disco transferido via streaming.

    Raises:
        HTTPException: Quando a tarefa não existir, não estiver pronta ou o arquivo não existir.
    """
    job = task_manager.get_job(task_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarefa '{task_id}' não encontrada.",
        )

    if job.status != "ready" or not job.file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A mídia ainda não está pronta para download (status atual: {job.status}).",
        )

    if not job.file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O arquivo processado não foi encontrado no servidor.",
        )

    background_tasks.add_task(cleanup_file, job.file_path)

    media_mime = "audio/mpeg" if job.media_type == "audio" else "video/mp4"
    safe_filename = media_service.sanitize_filename(job.file_path.name)
    ascii_fallback = re.sub(r"[^\x20-\x7E]", "_", safe_filename)
    encoded_filename = quote(safe_filename)
    content_disposition = (
        f'attachment; filename="{ascii_fallback}"; filename*=UTF-8\'\'{encoded_filename}'
    )

    return FileResponse(
        path=str(job.file_path),
        filename=ascii_fallback,
        media_type=media_mime,
        headers={
            "Content-Disposition": content_disposition,
        },
    )



# Montagem do frontend SPA compilado, caso exista
frontend_dist_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist_path), html=True), name="frontend")
