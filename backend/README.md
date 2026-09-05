# Finnapp — Backend API

Backend em Python 3.12 com FastAPI, estruturado segundo os princípios de Clean Architecture / Hexagonal Architecture (ADR-003).

---

## Estrutura de Pastas

```
backend/
├── app/
│   ├── core/                  # Configurações globais, segurança, logs e exceções
│   │   ├── config.py          # Settings via pydantic-settings
│   │   └── ...
│   ├── domain/                # Regras de negócio puras (sem dependência externa)
│   │   ├── entities/          # Entidades de domínio
│   │   ├── value_objects/     # Value Objects
│   │   ├── repositories/      # Interfaces de repositório (Protocols/ABCs)
│   │   └── services/          # Serviços de domínio puros
│   ├── application/           # Casos de uso e orquestração
│   │   ├── use_cases/         # Implementação de use cases
│   │   └── dto/               # Data Transfer Objects
│   ├── infrastructure/        # Implementações concretas de I/O
│   │   ├── db/                # SQLAlchemy models, repositórios concretos e sessão async
│   │   ├── pluggy/            # Cliente Pluggy e handlers
│   │   ├── cache/             # Cache em memória
│   │   └── scheduler/         # APScheduler
│   └── presentation/          # Camada web / endpoints FastAPI
│       ├── api/v1/routers/    # Rotas da API v1
│       └── main.py            # Entrypoint FastAPI
├── tests/
│   ├── unit/                  # Testes unitários
│   └── integration/           # Testes de integração
├── Dockerfile                 # Multi-stage Dockerfile
├── docker-compose.yml         # Ambiente local (API + PostgreSQL)
├── docker-compose.test.yml    # PostgreSQL efêmero para testes
├── pyproject.toml             # Gerenciamento de dependências via uv
└── .env.example               # Modelo de variáveis de ambiente
```

---

## Desenvolvimento Local

### 1. Pré-requisitos
- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

### 2. Instalação e Execução

```bash
# Copiar variáveis de ambiente
cp .env.example .env

# Instalar dependências com uv
uv sync --all-extras

# Executar a API em modo desenvolvimento
uv run uvicorn app.presentation.main:app --reload --port 8000
```

Acesse:
- Endpoint Health: `http://localhost:8000/health`
- Documentação interativa: `http://localhost:8000/docs`

---

## Qualidade e Testes

```bash
# Linter (ruff)
uv run ruff check .

# Formatação (ruff format)
uv run ruff format --check .

# Checagem estática de tipos (mypy)
uv run mypy app

# Testes automatizados (pytest)
uv run pytest -v
```

---

## Execução com Docker

```bash
# Subir API e PostgreSQL
docker compose up --build

# Parar serviços
docker compose down
```
