"""Aplicação FastAPI para extração e download de mídias do YouTube."""

from pathlib import Path
import re
from typing import Optional
from urllib.parse import quote
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from vdownloader.api.schemas import HealthResponse, VideoInfoRequest, VideoInfoResponse
from vdownloader.services.downloader import MediaService

VERSION = "0.2.1"

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
def health_check() -> HealthResponse:
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


# Montagem do frontend SPA compilado, caso exista
frontend_dist_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist_path), html=True), name="frontend")
