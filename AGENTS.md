# Registro de Desenvolvimento e Agentes - vdownloader-pytube

Este documento mantém o histórico e sincronismo entre as diretrizes de desenvolvimento orientado a especificações (Spec-Driven Development), arquitetura do sistema e os deployments realizados.

## Diretrizes Ativas
1. **Padrão de Código Backend:** PEP 8 com type hints completos, docstrings Google Style em PT-BR.
2. **Gerenciador de Dependências:** `uv` para Python.
3. **Abordagem de Testes:** Test-Driven Development (TDD) via `pytest` para o backend e `vitest` para o frontend.
4. **Arquitetura Frontend:** React com Vite, TypeScript sem `any`, Tailwind CSS moderno e TanStack Query.
5. **Estrutura de Infraestrutura:** Padrão `/infra/docker` e `/infra/maintenance` com prevenção de conflitos de portas (portas 3000 e 8000 em uso no host; uso de portas livres 8088 / 3088).
6. **Fluxo Git:** Desenvolvimento em branch de feature (`feature/web-migration`), merge para `main`, tags de versão incrementais e push para repositório remoto.

## Histórico de Implementações e Deployments
- **2026-10-22:** Início da migração da CLI para aplicação web full-stack.
  - Criação da especificação arquitetural em `.gemini/GEMINI.md`.
  - Configuração da branch `feature/web-migration`.
  - Mapeamento de prevenção de portas ocupadas no host.
- **2026-10-22:** Implementação do Backend com FastAPI e TDD.
  - Testes com `pytest` criados antes do código (`tests/test_services.py` e `tests/test_api.py`).
  - Criação de `MediaService` em `vdownloader/services/downloader.py` com extração e conversão de vídeo/áudio via `yt-dlp`.
  - Criação de esquemas Pydantic em `vdownloader/api/schemas.py`.
  - Criação da aplicação FastAPI em `vdownloader/api/app.py` com endpoints `/api/health`, `/api/info` e `/api/download` com streaming e remoção de arquivo temporário pós-envio.
  - 100% dos testes unitários e de integração aprovados.
- **2026-10-22:** Implementação do Frontend com React, TypeScript, Tailwind CSS e Vitest.
  - Criação de componentes responsivos: `Navbar`, `UrlInput`, `MediaCard`, `DownloadOptionList`.
  - Suporte a extração e visualização em tela de miniatura, duração, autor, título e opções de qualidade.
  - Suporte a download de vídeos MP4 (1080p, 720p, 360p, HQ) e áudio MP3 para computador e celular.
  - Integração com `@tanstack/react-query` para gerenciamento de estado assíncrono.
  - Testes unitários com Vitest em `frontend/src/__tests__/` (100% aprovados).
  - Build de produção compilado com sucesso.
- **2026-10-22:** Configuração de Infraestrutura e Docker.
  - Implementação da estrutura `/infra/docker` com `Dockerfile` multi-stage (Node.js + Python 3.12 slim com ffmpeg e uv), `docker-compose.yml` e `env-example`.
  - Configuração de isolamento de portas na porta 8088 para evitar conflitos com as portas 3000 e 8000 ativas no host.
  - Implementação da estrutura `/infra/maintenance` com `docker-cleanup.sh`, `docker-cleanup.service`, `docker-cleanup.timer` e `readme.md`.
- **2026-10-22:** Deploy e Validação da Versão v0.2.0.
  - Execução da aplicação via Docker Compose validada com sucesso na porta 8088 (`running (healthy)`).
  - Testes do backend (pytest) e frontend (vitest) aprovados com 100% de cobertura dos novos fluxos.
  - Merge para a branch `main` e criação da tag de versão `0.2.0`.
- **2026-10-22:** Correção de Extração/Encoding e Seleção de Diretório via Explorer (v0.2.1).
  - Diagnóstico e correção do erro de codificação `latin-1` gerado por caracteres unicode especiais (`\uff5c` e barras verticais) presentes no título do vídeo `https://www.youtube.com/watch?v=41IOkVjy3MM`.
  - Implementação de sanitização de nomes de arquivos em `MediaService.sanitize_filename` e cabeçalho `Content-Disposition` em conformidade com RFC 5987 / RFC 6266 com fallback ASCII seguro e UTF-8 percent-encoded.
  - Resiliência na extração de áudio caso o host não possua o binário do `ffmpeg`.
  - Implementação da janela nativa do Explorer para seleção de diretório de armazenamento no frontend utilizando a **File System Access API** (`window.showSaveFilePicker`). Ao clicar em Baixar, o navegador abre o gerenciador de arquivos nativo (Explorer/Finder) para o usuário escolher onde deseja armazenar a mídia, com barra de progresso em tempo real e fallback tradicional para mobile.
  - Suíte de testes do backend atualizada para 11 testes aprovados e testes do frontend aprovados.
- **2026-10-22:** Limpeza de Código Legado e Preparação para Fly.io (v0.2.2).
  - Remoção dos arquivos e pastas desnecessárias: `requirements.txt`, `setup.py`, `MANIFEST.in` e `vdownloader/media/`.
  - Remoção de import desnecessário de `MEDIA_PATH` em `vdownloader/services/downloader.py`.
  - Atualização do `vdownloader/__main__.py` para inicializar o servidor FastAPI com suporte opcional à flag `--cli`.
  - Criação da especificação de deploy no Fly.io em `fly.toml` com porta interna 8088, healthcheck, auto-start/stop e 1GB de RAM dimensionada para ffmpeg e yt-dlp.
  - Validação dos 11 testes pytest e 5 testes vitest.
- **2026-10-22:** Inicialização do App Fly.io e Geração de Configurações (v0.2.3).
  - Configuração do aplicativo `vdtube` no Fly.io associado à região `gru` (São Paulo).
  - Adição do arquivo `.dockerignore` otimizado para o processo de build do Fly.io.
  - Sincronização dos parâmetros de runtime com portas expostas e verificações de integridade.
