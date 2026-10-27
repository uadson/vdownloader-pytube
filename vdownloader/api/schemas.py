"""Esquemas de dados Pydantic para validação e serialização da API."""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class VideoInfoRequest(BaseModel):
    """Modelo de entrada para consulta de informações do vídeo."""

    url: str = Field(
        ...,
        min_length=5,
        description="Endereço URL do vídeo a ser consultado.",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )


class DownloadOption(BaseModel):
    """Modelo descritivo de uma opção de download (vídeo ou áudio)."""

    format_id: str = Field(..., description="Identificador único da opção de download.")
    label: str = Field(..., description="Rótulo legível para exibição ao usuário.")
    media_type: str = Field(..., description="Tipo de mídia ('video' ou 'audio').")
    resolution: Optional[str] = Field(None, description="Resolução do vídeo, quando aplicável.")
    ext: str = Field(..., description="Extensão final do arquivo gerado.")
    is_audio: bool = Field(..., description="Indica se é uma extração de áudio exclusiva.")


class VideoInfoResponse(BaseModel):
    """Modelo de resposta com os metadados extraídos do vídeo."""

    id: Optional[str] = Field(None, description="ID do vídeo na plataforma de origem.")
    title: str = Field(..., description="Título do vídeo.")
    author: str = Field(..., description="Nome do canal ou autor do vídeo.")
    duration: int = Field(..., description="Duração total em segundos.")
    duration_formatted: str = Field(..., description="Duração formatada em HH:MM:SS ou MM:SS.")
    thumbnail: str = Field(..., description="URL da miniatura do vídeo.")
    description: str = Field(..., description="Descrição do vídeo.")
    url: str = Field(..., description="URL original do vídeo consultado.")
    options: List[DownloadOption] = Field(
        ...,
        description="Lista de opções de download suportadas para este vídeo.",
    )


class HealthResponse(BaseModel):
    """Modelo de resposta para o status da API."""

    status: str = Field("ok", description="Status operacional do serviço.")
    version: str = Field(..., description="Versão atual do software vdownloader.")


class DownloadJobRequest(BaseModel):
    """Modelo de entrada para inicialização de tarefa assíncrona de download."""

    url: str = Field(
        ...,
        min_length=5,
        description="Endereço URL do vídeo a ser baixado.",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )
    media_type: str = Field(
        "video",
        pattern="^(video|audio)$",
        description="Tipo de mídia desejada ('video' ou 'audio').",
    )
    resolution: Optional[str] = Field(
        "best",
        description="Resolução desejada ('360p', '720p', '1080p', 'best').",
    )


class DownloadJobStatus(BaseModel):
    """Modelo de resposta para consulta de status da tarefa de download."""

    task_id: str = Field(..., description="Identificador único da tarefa de download.")
    status: str = Field(
        ...,
        description="Estado atual da tarefa ('pending', 'downloading', 'processing', 'ready', 'failed').",
    )
    progress: float = Field(0.0, description="Progresso percentual do download (0 a 100).")
    message: Optional[str] = Field(None, description="Mensagem descritiva do estado atual.")
    filename: Optional[str] = Field(None, description="Nome do arquivo gerado quando concluído.")
    error: Optional[str] = Field(None, description="Mensagem de erro caso a tarefa tenha falhado.")

