#!/usr/bin/env bash
# ==============================================================================
# Script de manutenção e limpeza periódica do ambiente Docker
# ==============================================================================

set -euo pipefail

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando rotina de limpeza do Docker..."

# Remove containers com status exited
EXITED_CONTAINERS=$(docker ps -a -q -f status=exited)
if [ -n "$EXITED_CONTAINERS" ]; then
    echo "Removendo containers inativos..."
    docker rm -v $EXITED_CONTAINERS
fi

# Remove imagens órfãs (dangling)
DANGLING_IMAGES=$(docker images -q -f dangling=true)
if [ -n "$DANGLING_IMAGES" ]; then
    echo "Removendo imagens órfãs (dangling)..."
    docker rmi $DANGLING_IMAGES
fi

# Limpa volumes não utilizados
echo "Limpando volumes não referenciados..."
docker volume prune -f

# Limpa cache do builder com mais de 7 dias
echo "Limpando cache de build expirado..."
docker builder prune -f --filter "until=168h"

# Limpa mídias temporárias com mais de 24 horas no diretório temporário local, se existir
if [ -d "/tmp/vdownloader_media" ]; then
    echo "Limpando arquivos temporários de download antigos..."
    find /tmp/vdownloader_media -type f -mmin +60 -delete 2>/dev/null || true
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Rotina de limpeza finalizada com sucesso."
