# vDownloader

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF.svg)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

Aplicação web moderna, rápida e responsiva para extração de informações e download de vídeos e áudios do YouTube em alta definição (Full HD 1080p, HD 720p, 360p e MP3). Projetada para funcionar tanto em computadores quanto em dispositivos móveis.

---

## 🚀 Tecnologias

- **Backend:** [FastAPI](https://fastapi.tiangolo.com) + [yt-dlp](https://github.com/yt-dlp/yt-dlp) + Pydantic v2
- **Gerenciamento de Dependências:** [uv](https://docs.astral.sh/uv/)
- **Frontend:** [React](https://react.dev) + [TypeScript](https://www.typescriptlang.org/) + [Vite](https://vitejs.dev)
- **Estilização:** [Tailwind CSS](https://tailwindcss.com) (Design Premium com Dark Mode)
- **Gerenciamento de Estado:** [TanStack Query v5](https://tanstack.com/query/latest)
- **Testes Automatizados:** [pytest](https://pytest.org) (Backend) e [Vitest](https://vitest.dev) (Frontend)
- **Infraestrutura:** Docker e Docker Compose com prevenção automática de conflitos de portas

---

## 📦 Como Executar via Docker (Recomendado)

O projeto possui configuração pronta para execução conteinerizada sem conflitos de portas:

```bash
# 1. Navegue até o diretório de infraestrutura Docker
cd infra/docker

# 2. Crie o arquivo .env a partir do exemplo (se ainda não existir)
cp env-example .env

# 3. Construa e suba o container
docker compose up -d
```

Acesse a aplicação no navegador em:
👉 **[http://localhost:8088](http://localhost:8088)**

> **Nota:** A aplicação roda na porta `8088` por padrão, evitando colisões com outros serviços ativos nas portas 3000 e 8000.

---

## 🛠️ Desenvolvimento Local

### Backend (Python com `uv`)

1. Crie o ambiente virtual e instale as dependências:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

2. Execute os testes com pytest:
   ```bash
   pytest
   ```

3. Inicie o servidor FastAPI:
   ```bash
   uvicorn vdownloader.api.app:app --host 0.0.0.0 --port 8088 --reload
   ```

### Frontend (React + Vite)

1. Acesse a pasta do frontend e instale as dependências:
   ```bash
   cd frontend
   npm install
   ```

2. Execute os testes com Vitest:
   ```bash
   npm test
   ```

3. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

---

## 🧪 Estrutura de Testes

- **Backend:** `tests/test_services.py` e `tests/test_api.py` (Test-Driven Development com pytest).
- **Frontend:** `frontend/src/__tests__/UrlInput.test.tsx` e `frontend/src/__tests__/MediaCard.test.tsx` (Vitest + Testing Library).

---

## 🧹 Rotinas de Manutenção

Localizadas em `infra/maintenance`:
- `docker-cleanup.sh`: Script para remoção de containers inativos, imagens dangling e mídias temporárias expiradas.
- `docker-cleanup.service` & `docker-cleanup.timer`: Unidades systemd para agendamento diário automático.

---

## 📄 Licença

Distribuído sob a licença [MIT](LICENSE).
