# Especificações do Projeto vdownloader-pytube

## 1. Visão Geral
Migração e refatoração do software **vdownloader-pytube** de uma aplicação exclusivamente CLI para uma aplicação web moderna, responsiva (computador e celular), utilizando **FastAPI** no backend e **React + Vite + TypeScript + Tailwind CSS + TanStack Query** no frontend.

## 2. Requisitos Arquiteturais
- **Linguagem Backend:** Python 3.11+
- **Padrão de Código:** PEP 8, 4 espaços de indentação, Type Hints em todas as funções.
- **Docstrings:** Formato Google Style em Português do Brasil (PT-BR).
- **Gerenciador de Pacotes:** `uv`.
- **Testes Backend:** Test-Driven Development (TDD) obrigatório com `pytest`.
- **Frontend:** React + Vite, TypeScript rigoroso (sem `any`), Tailwind CSS (design Premium), TanStack Query para gerenciamento de estado assíncrono.
- **Testes Frontend:** Vitest na pasta `frontend/src/__tests__/`.
- **Estrutura de Deploy e Infraestrutura:** Docker e Docker Compose na pasta `/infra/docker` e rotinas de manutenção em `/infra/maintenance`.
- **Resolução de Conflitos de Portas:** Verificação prévia de portas livres no host (portas 3000 e 8000 identificadas em uso; mapeamento padrão nas portas 8088 e 3088).

## 3. Especificação dos Endpoints da API
- `GET /api/health`: Verificação de integridade do serviço.
- `POST /api/info`: Recebe `{ "url": "..." }`, valida e retorna metadados completos do vídeo (título, autor, duração, thumbnail, descrição e opções de download de áudio e vídeo).
- `GET /api/download`: Endpoint de download direto para o navegador com cabeçalho `Content-Disposition`, suportando parâmetros de URL, tipo (`video` ou `audio`) e resolução (`360p`, `720p`, `1080p`, `hq`).

## 4. Estado Atual dos Módulos Backend
- `vdownloader.services.downloader.MediaService`: Extração assíncrona/síncrona de metadados e orquestração de download com yt-dlp/ffmpeg.
- `vdownloader.api.schemas`: Modelos de dados Pydantic com validação tipada e documentação integrada.
- `vdownloader.api.app`: Servidor FastAPI com CORS, middleware, streaming e background tasks para limpeza segura de arquivos.
- Testes automatizados: 10 testes com pytest passando em `tests/`.

## 5. Estado Atual dos Módulos Frontend
- React 18 + Vite + TypeScript (modo estrito sem uso de `any`).
- Tailwind CSS com tema moderno (paleta dark/violet/slate com suporte responsivo a mobile e desktop).
- TanStack Query v5 orquestrando chamadas e cache da API.
- Testes unitários com Vitest (5 testes em `UrlInput.test.tsx` e `MediaCard.test.tsx`).
- Build de produção verificado com sucesso (`frontend/dist`).

## 6. Infraestrutura e Manutenção
- Dockerfile multi-stage com compilação de assets estáticos e runtime em Python 3.12 com suporte a ffmpeg para processamento e conversão de áudio.
- Docker Compose configurado com volumes isolados e healthcheck nativo na porta 8088.
- Scripts de manutenção preventiva e unidades systemd sob `infra/maintenance/`.

## 7. Status do Deployment (v0.2.1)
- Correção de erro na extração de títulos com caracteres unicode fora da tabela latin-1 (ex: barras fullwidth `\uff5c`) com sanitização e encoding compatível com RFC 5987 / RFC 6266.
- Implementação de seleção de diretório no navegador através da File System Access API nativa do sistema operacional (Explorer), permitindo ao usuário indicar a pasta onde deseja salvar o vídeo ou áudio.
- Container `vdownloader-app` em execução ativa no host com status saudável na porta `8088`.
- Suíte de testes: 11 testes pytest + 5 testes vitest executados com 100% de sucesso.





