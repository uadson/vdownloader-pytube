# Stage 1: Build da interface frontend com Node
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Backend Python e runtime de produção
FROM python:3.12-slim

# Instalação do ffmpeg e dependências do sistema necessárias para extração de áudio e vídeo
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalação do uv para gerenciamento rápido de dependências
COPY --from=ghcr.io/astral-sh/uv:0.5.26 /uv /uvx /bin/

# Instalação das dependências do backend
COPY pyproject.toml README.md ./
COPY vdownloader/ ./vdownloader/

RUN uv pip install --system --no-cache -e .

# Copia os arquivos compilados do frontend para servir via FastAPI
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Criação do diretório de mídia temporário com permissões
RUN mkdir -p /tmp/vdownloader_media && chmod 777 /tmp/vdownloader_media

ENV PORT=8088
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

EXPOSE 8088

# Inicialização com uvicorn
CMD ["sh", "-c", "uvicorn vdownloader.api.app:app --host 0.0.0.0 --port ${PORT}"]
