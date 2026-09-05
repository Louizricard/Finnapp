# Finnapp — Sistema Pessoal de Controle Financeiro

Monorepo do **Finnapp**, uma plataforma completa de gestão financeira pessoal com sincronização Open Finance (via Pluggy), categorização inteligente, gestão orçamentária e relatórios patrimoniais.

---

## Estrutura do Monorepo

O projeto adota uma arquitetura de monorepo (ADR-006) com separação estrita de responsabilidades:

```
Finnapp/
├── backend/               # API FastAPI (Python 3.12, Clean Architecture, SQLAlchemy, Alembic)
│   ├── app/               # Código-fonte (core, domain, application, infrastructure, presentation)
│   ├── tests/             # Testes unitários e de integração (pytest)
│   ├── Dockerfile         # Multi-stage Dockerfile
│   ├── docker-compose.yml # Compose com API + PostgreSQL 16
│   └── pyproject.toml     # Dependências gerenciadas via uv
├── app/                   # Aplicativo Flutter (Android + Web, Feature-First, Riverpod)
│   ├── lib/               # Código-fonte (core, features, shared)
│   ├── test/              # Testes de widget e unitários
│   └── pubspec.yaml       # Dependências Flutter
├── .github/workflows/     # Pipelines de CI/CD (backend-ci.yml, app-ci.yml)
├── docs/                  # Guias e documentação de arquitetura
├── PRD_App_Financeiro.md  # Documento de Requisitos de Produto (PRD)
└── Sprints_App_Financeiro.md # Planejamento e detalhamento de Sprints
```

---

## Pré-requisitos

- **Docker & Docker Compose**: v24+ / Compose v2+
- **Python**: 3.12+ com [uv](https://github.com/astral-sh/uv)
- **Flutter**: 3.24+ (Dart 3.x)
- **Google Chrome** (para execução web do Flutter)

---

## Como Rodar o Backend

### 1. Usando Docker Compose (Recomendado para Dev)

```bash
cd backend
cp .env.example .env
docker compose up --build
```

A API estará disponível em:
- Health Check: `http://localhost:8000/health`
- Documentação Swagger: `http://localhost:8000/docs`
- Documentação Redoc: `http://localhost:8000/redoc`

### 2. Rodando Localmente com `uv`

```bash
cd backend
cp .env.example .env

# Sincronizar dependências
uv sync

# Executar a API com auto-reload
uv run uvicorn app.presentation.main:app --reload --port 8000
```

### 3. Qualidade de Código e Testes no Backend

```bash
cd backend

# Linter e Formatação
uv run ruff check .
uv run ruff format --check .

# Verificação Estrita de Tipos
uv run mypy app

# Testes Automatizados
uv run pytest
```

---

## Como Rodar o Frontend (Flutter)

### 1. Executando no Chrome (Web)

```bash
cd app
flutter pub get

# Se Chrome estiver em flatpak ou caminho customizado, defina CHROME_EXECUTABLE:
# export CHROME_EXECUTABLE=/var/lib/flatpak/exports/bin/com.google.Chrome

flutter run -d chrome
```

### 2. Verificação de Código e Testes no Frontend

```bash
cd app

# Análise estática de código
flutter analyze

# Execução dos testes
flutter test
```

---

## Integração com a Pluggy

Para configurar credenciais de Sandbox da Pluggy e entender o fluxo de desenvolvimento e transição para o Meu Pluggy, consulte o [Guia de Configuração da Pluggy](docs/pluggy_setup_guide.md).

---

## Licença

Projeto para uso pessoal privado. Todos os direitos reservados.