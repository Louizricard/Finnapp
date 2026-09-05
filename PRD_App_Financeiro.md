# PRD — Aplicativo de Gerenciamento Financeiro Pessoal

**Codinome do projeto:** `finapp`
**Tipo de documento:** Product Requirements Document técnico, para consumo por agente de programação (ex: Claude Code) e execução autônoma do projeto do início ao fim.
**Versão:** 1.0
**Autor:** Documento gerado com o usuário (proprietário único do produto)

---

## 0. Sobre este documento

Este PRD é **a fonte única de verdade** para a construção do `finapp`. Ele foi escrito para ser interpretado e executado por um agente de programação, portanto:

- Toda decisão técnica relevante foi tomada e justificada aqui — o agente **não deve reabrir decisões de arquitetura** já definidas (stack, banco de dados, padrão de camadas) sem necessidade real.
- Onde há ambiguidade proposital (para o agente decidir em tempo de implementação), isso é marcado explicitamente como `[DECISÃO DO AGENTE]`.
- O projeto **não é um MVP**: o padrão de qualidade é o de um app que iria para produção real (testes, CI/CD, tratamento de erros, logging, segurança, documentação). A simplificação permitida é de **escopo/infraestrutura** (por ser uso pessoal e de um único usuário), nunca de **qualidade de engenharia**.
- Convenção de nomenclatura no documento: `RF-XXX` = Requisito Funcional, `RNF-XXX` = Requisito Não-Funcional, `ADR-XXX` = Architecture Decision Record.

---

## 1. Visão Geral do Produto

### 1.1 Contexto e Motivação

O usuário é ao mesmo tempo o dono do produto e seu único usuário final. Ele possui conta(s) no **Banco Inter** e quer centralizar sua vida financeira (extratos, cartão de crédito, categorização de gastos, orçamentos, metas e contas a pagar) em um aplicativo próprio, com dados sincronizados automaticamente via Open Finance, em vez de depender de apps de terceiros ou planilhas manuais.

### 1.2 Objetivo

Construir um aplicativo **Flutter (Android + Web)**, com backend próprio em arquitetura **BFF (Backend for Frontend)**, que:

1. Conecta-se ao Banco Inter (e, potencialmente, outras instituições no futuro) via **Pluggy/Open Finance**, usando o programa gratuito **Meu Pluggy** (uso pessoal, sem custo, sem prazo de expiração).
2. Sincroniza automaticamente contas, saldos, cartão de crédito e transações.
3. Categoriza transações automaticamente (regras + categoria vinda da Pluggy), permitindo ajuste manual.
4. Permite orçamentos por categoria, metas financeiras e controle de contas a pagar/lembretes.
5. Apresenta dashboards e relatórios (fluxo de caixa, gasto por categoria, evolução patrimonial).
6. Mantém os dados e segredos sensíveis exclusivamente no backend, nunca no cliente.

### 1.3 Público-alvo / Persona

Único usuário: o próprio desenvolvedor/proprietário. Ainda assim, o sistema é modelado com uma tabela `users` formal (não hardcoded), para:
- Permitir a troca de senha/token com segurança normal de produção.
- Deixar a porta aberta para um segundo usuário no futuro (ex: cônjuge) sem redesenho de schema — embora **multi-tenancy completo não seja requisito agora** (ver `1.4`).

### 1.4 Escopo

**Dentro do escopo (obrigatório):**
- App Flutter rodando em **Android** e **Web** (mesma base de código).
- Backend BFF em **Python + FastAPI**.
- Autenticação própria do app (usuário/senha + JWT) com trava adicional local (PIN/biometria no Android).
- Integração completa com Pluggy (sandbox → Meu Pluggy em produção) para o Banco Inter.
- CRUD completo de: contas, transações (sync + manuais), categorias, regras de categorização, orçamentos, metas, contas a pagar/lembretes.
- Dashboards e relatórios com gráficos.
- Sincronização via webhook + fallback de sincronização periódica.
- Exportação de dados (CSV no mínimo; PDF como diferencial).
- Testes automatizados (backend e frontend), CI/CD, containerização, documentação.

**Fora do escopo (não construir agora):**
- Multi-tenancy real com onboarding de múltiplos usuários pagantes.
- iOS (arquitetura deve permitir adicionar depois sem refatoração grande, já que é Flutter, mas não é entregável desta fase).
- Pagamentos/iniciação de pagamento via Pix pela Pluggy (somente leitura de dados nesta fase).
- Investimentos detalhados (renda fixa/variável) — schema deve comportar no futuro, mas telas não são obrigatórias agora.
- Assistente conversacional com LLM (mencionado como possível evolução futura na seção de Roadmap, não é requisito desta versão).

### 1.5 Premissas e Decisões Assumidas

Estas decisões foram tomadas para que o agente de programação não precise voltar a perguntar. Estão sinalizadas ao longo do documento como `ADR`.

| # | Decisão | Escolhido |
|---|---|---|
| 1 | Linguagem/framework do backend | **Python 3.12 + FastAPI** |
| 2 | Hospedagem | **PaaS gerenciado** (Railway, Render ou Fly.io — projeto entregue via Docker para ser portável entre os três) |
| 3 | Plataformas do app | **Android + Web** (mesma base Flutter) |
| 4 | Banco de dados | **PostgreSQL** (gerenciado pela própria PaaS) |
| 5 | Cache/fila | **Nenhum serviço externo obrigatório** — cache em processo e agendador embutido (ver ADR-004), por ser uso pessoal de baixo volume |
| 6 | State management Flutter | **Riverpod** (com geração de código) |
| 7 | Agregador Open Finance | **Pluggy**, via programa gratuito **Meu Pluggy** |
| 8 | Repositório | **Monorepo** (`/backend` + `/app`) |

---

## 2. Glossário

| Termo | Definição |
|---|---|
| **BFF** | Backend for Frontend: camada de backend própria que concentra segredos, regras de negócio e orquestração de APIs externas, exposta ao cliente Flutter como uma API única e coesa. |
| **Item (Pluggy)** | Representa uma conexão entre o usuário e uma instituição financeira (ex: "Inter" conectado via Open Finance). Todo dado (contas, transações) pertence a um Item. |
| **Connector (Pluggy)** | Configuração de integração de uma instituição financeira específica dentro da Pluggy. |
| **Connect Token** | Token de curta duração (30 min) gerado pelo backend, usado **apenas no cliente** para autorizar o widget Pluggy Connect. Não dá acesso a dados, só ao fluxo de conexão. |
| **API Key (Pluggy)** | Token de longa duração relativa (2h), usado **apenas no backend**, com acesso total à API da Pluggy. Nunca deve chegar ao cliente. |
| **Pluggy Connect** | Widget hospedado pela Pluggy que conduz o usuário pelo fluxo de autorização bancária (Open Finance ou credenciais diretas). |
| **Open Finance** | Sistema regulado pelo Banco Central do Brasil que permite compartilhamento de dados financeiros mediante consentimento explícito do usuário, diretamente pelo app do banco. |
| **Meu Pluggy** | Programa gratuito e sem prazo de expiração da Pluggy voltado a projetos pessoais/desenvolvedores, permitindo uso real da API sem os planos comerciais pagos. |
| **Webhook** | Notificação HTTP enviada pela Pluggy ao backend quando um evento ocorre (nova transação, item atualizado, erro de conexão etc.), evitando polling constante. |
| **BFF Sync Job** | Rotina agendada no próprio backend que garante consistência dos dados mesmo se um webhook falhar. |

---

## 3. Arquitetura de Alto Nível

### 3.1 Visão C4 — Contexto e Contêineres

```mermaid
C4Context
title Diagrama de Contexto — finapp

Person(user, "Usuário", "Dono e único usuário do app")
System(finapp_app, "finapp (Flutter)", "App Android/Web de gestão financeira")
System(finapp_bff, "finapp BFF (FastAPI)", "Backend próprio: regras de negócio, auth, orquestração")
System_Ext(pluggy, "Pluggy API", "Agregador Open Finance")
System_Ext(inter, "Banco Inter", "Instituição financeira do usuário, via Open Finance")

Rel(user, finapp_app, "Usa")
Rel(finapp_app, finapp_bff, "Consome API REST (HTTPS/JWT)")
Rel(finapp_bff, pluggy, "Autentica, cria connectToken, consulta contas/transações, recebe webhooks")
Rel(pluggy, inter, "Coleta dados via Open Finance, mediante consentimento do usuário")
```

```mermaid
C4Container
title Diagrama de Contêineres — finapp

Person(user, "Usuário")

Container_Boundary(client, "Cliente") {
  Container(app, "App Flutter", "Dart/Flutter", "Android + Web. UI, estado (Riverpod), cache local leve")
}

Container_Boundary(backend, "Backend (BFF)") {
  Container(api, "API FastAPI", "Python 3.12", "REST API v1, autenticação JWT, regras de negócio")
  Container(scheduler, "Scheduler embutido", "APScheduler (in-process)", "Sync fallback periódico, verificação de contas a pagar")
  ContainerDb(db, "PostgreSQL", "SQL", "Dados do usuário: contas, transações, categorias, orçamentos, metas")
}

System_Ext(pluggy, "Pluggy API", "Open Finance aggregator")

Rel(user, app, "Usa")
Rel(app, api, "HTTPS + JWT")
Rel(api, db, "SQLAlchemy async / asyncpg")
Rel(api, pluggy, "REST (apiKey) — contas, transações, connect_token")
Rel(pluggy, api, "Webhooks (item/*, transactions/*)")
Rel(scheduler, api, "Roda na mesma app, chama use cases internos")
```

### 3.2 Decisões de Arquitetura (ADRs resumidos)

**ADR-001 — Por que BFF mesmo com um único tipo de "cliente lógico" (Flutter)?**
Mesmo com Android+Web compartilhando código Flutter, o BFF se justifica porque: (a) os segredos da Pluggy (`CLIENT_ID`/`CLIENT_SECRET`/apiKey) **jamais** podem estar no app, dado que Flutter Web expõe todo código-fonte ao navegador; (b) a lógica de categorização, cálculo de orçamento e agregação de relatórios deve rodar em um único lugar controlado; (c) Web e Android têm fluxos de conexão Pluggy diferentes (iframe/redirect vs. WebView) — o BFF abstrai isso emitindo sempre um `connectToken` e recebendo sempre um `itemId`, independente da plataforma de origem.

**ADR-002 — Por que Python/FastAPI?**
Escolha do usuário. FastAPI oferece tipagem via Pydantic, geração automática de OpenAPI/Swagger (documentação viva), suporte assíncrono nativo (importante pois toda chamada à Pluggy é I/O-bound) e ótimo ecossistema de testes.

**ADR-003 — Clean Architecture / Hexagonal no backend**
Optou-se por separar `domain` (regras de negócio puras, sem dependência de framework), `application` (casos de uso), `infrastructure` (implementações concretas: banco, Pluggy, cache) e `presentation` (rotas FastAPI). Isso garante que a lógica de negócio (ex: "como categorizar uma transação", "quando um orçamento estourou") seja testável sem subir banco de dados ou mockar HTTP.

**ADR-004 — Sem Redis/Celery obrigatórios**
Dado tratar-se de uso pessoal com um único usuário e baixíssimo volume de requisições, optou-se por **não** exigir Redis nem uma fila de tarefas externa (Celery/RQ) na v1. Em vez disso:
- O `apiKey` da Pluggy (TTL 2h) é cacheado **em memória do processo**, com renovação proativa a cada ~90 minutos.
- Jobs periódicos (sync de fallback, verificação de contas a pagar) rodam via **APScheduler embutido no mesmo processo FastAPI**.
- Trade-off aceito: se o backend escalar para múltiplas instâncias no futuro, esse cache em memória e o scheduler in-process deixam de ser suficientes (cada instância teria seu próprio agendador rodando duplicado). Nesse cenário, migrar para Redis + APScheduler com `RedisJobStore` (ou Celery) é a evolução natural — a interface `PluggyTokenCache` já é abstraída via porta/repositório para tornar essa troca trivial (ver `3.3`).

**ADR-005 — Riverpod no Flutter**
Escolhido por ser o padrão recomendado atualmente pelo time do Flutter, ter melhor testabilidade que Provider/GetX, suportar geração de código (menos boilerplate) e lidar bem com estados assíncronos (streams de sincronização, refresh de dados).

**ADR-006 — Monorepo**
Um único repositório Git com `/backend` e `/app` nas raízes, cada um com seu próprio pipeline de CI, facilita versionamento conjunto de contrato de API (schema compartilhado) e é mais simples de operar sozinho.

### 3.3 Arquitetura em Camadas — Backend

```
Presentation (FastAPI routers, Pydantic schemas)
        ↓ chama
Application (Use Cases — orquestram regras de negócio)
        ↓ depende de interfaces (Ports)
Domain (Entidades, Value Objects, regras puras, interfaces de repositório)
        ↑ implementado por
Infrastructure (SQLAlchemy repos, Pluggy client, cache em memória, scheduler)
```

Regra de dependência: **camadas internas nunca conhecem camadas externas**. `domain/` não importa nada de `infrastructure/` ou `presentation/`. A inversão de dependência é feita via injeção (FastAPI `Depends`), com interfaces (`Protocol`/ABC) definidas em `domain/repositories/` e implementadas em `infrastructure/db/repositories/`.

### 3.4 Arquitetura em Camadas — Frontend (Flutter)

Organização **feature-first**, cada feature com 3 sub-camadas:

```
lib/features/<feature>/
  data/         → datasources (Dio), DTOs (freezed+json_serializable), implementação de repositório
  domain/       → entidades, interfaces de repositório, use cases (opcional para regras simples)
  presentation/ → providers Riverpod (estado), screens, widgets
```

Comunicação entre features (ex: `dashboard` lendo dados de `transactions`) acontece via **providers Riverpod expostos publicamente pela feature dona do dado**, nunca por acesso direto a `data/` de outra feature.

---

## 4. Stack Tecnológica

### 4.1 Backend

| Categoria | Escolha | Observação |
|---|---|---|
| Linguagem | Python 3.12+ | |
| Framework web | FastAPI | ASGI, tipagem via Pydantic v2 |
| Servidor ASGI | Uvicorn (workers gerenciados pela PaaS) | |
| ORM | SQLAlchemy 2.0 (modo assíncrono) | + `asyncpg` como driver |
| Migrations | Alembic | Autogeração + revisão manual obrigatória |
| Banco de dados | PostgreSQL 16 | Instância gerenciada da PaaS |
| Validação/Serialização | Pydantic v2 | Schemas de request/response |
| Cliente HTTP (p/ Pluggy) | `httpx` (async) | |
| Autenticação | JWT (`python-jose` ou `pyjwt`) + `passlib[argon2]` | Access token curto + refresh token |
| Rate limiting | `slowapi` | Endpoints de auth e webhook |
| Agendador | `APScheduler` (in-process, `AsyncIOScheduler`) | Ver ADR-004 |
| Logging | `structlog` (JSON estruturado) | |
| Monitoramento de erros | `sentry-sdk` (plano free) | |
| Testes | `pytest`, `pytest-asyncio`, `httpx.AsyncClient`, `respx` (mock de chamadas Pluggy), `factory_boy`, `faker` | |
| Qualidade de código | `ruff` (lint + format), `mypy` (checagem de tipos) | Rodar em pre-commit e CI |
| Empacotamento | `pyproject.toml` (Poetry ou `uv`) | Recomenda-se `uv` por velocidade |
| Containerização | Docker (multi-stage build) | Imagem final baseada em `python:3.12-slim` |

### 4.2 Frontend (Flutter)

| Categoria | Escolha | Observação |
|---|---|---|
| Framework | Flutter (canal stable mais recente) | Dart 3.x, null-safety |
| Plataformas alvo | Android, Web | iOS não configurado nesta fase |
| Gerenciamento de estado | `flutter_riverpod` + `riverpod_generator` + `riverpod_annotation` | Providers gerados via `build_runner` |
| Roteamento | `go_router` | Rotas nomeadas, guards de autenticação |
| Cliente HTTP | `dio` | Interceptors para JWT, refresh automático, logging |
| Modelos imutáveis | `freezed` + `json_serializable` | |
| Armazenamento seguro (Android) | `flutter_secure_storage` | Keystore do Android |
| Armazenamento (Web) | **Não usar `localStorage`/`sessionStorage` para tokens.** Ver seção 11.2 (estratégia específica para Web). | |
| Gráficos | `fl_chart` | Pizza (gasto por categoria), linha (evolução patrimonial), barras (fluxo de caixa) |
| Biometria/PIN (Android) | `local_auth` | Trava de app opcional além do login |
| Notificações locais (Android) | `flutter_local_notifications` | Lembretes de contas a pagar |
| WebView (Android, fluxo Pluggy Connect) | `flutter_inappwebview` | Baseado no quickstart oficial da Pluggy para Flutter |
| Internacionalização/formatação | `intl` | Moeda `pt_BR`, datas `dd/MM/yyyy` |
| Ícones | `lucide_icons` ou `flutter_lucide` | Consistência visual |
| Testes | `flutter_test`, `mocktail`, `integration_test`, `golden_toolkit` (opcional) | |
| Lint | `very_good_analysis` ou `flutter_lints` estendido | |

### 4.3 Infraestrutura e Terceiros

| Item | Escolha |
|---|---|
| Hospedagem backend + banco | Railway, Render **ou** Fly.io (Dockerfile único, portável entre as três) |
| Open Finance | Pluggy — ambiente **Sandbox** em desenvolvimento, **Meu Pluggy** em uso real/produção |
| Monitoramento de erros | Sentry (plano gratuito) |
| CI/CD | GitHub Actions |
| Distribuição do app Android | Build de APK/AAB assinado, distribuído manualmente (sem Play Store nesta fase) |
| Distribuição do app Web | Build `flutter build web`, hospedado como estático (mesma PaaS do backend ou Cloudflare Pages/Vercel) |

---

## 5. Modelo de Dados

### 5.1 Diagrama Entidade-Relacionamento (simplificado)

```mermaid
erDiagram
    USERS ||--o{ PLUGGY_ITEMS : possui
    USERS ||--o{ ACCOUNTS : possui
    USERS ||--o{ CATEGORIES : cria
    USERS ||--o{ BUDGETS : define
    USERS ||--o{ GOALS : define
    USERS ||--o{ BILLS : define
    USERS ||--o{ NOTIFICATIONS : recebe
    PLUGGY_ITEMS ||--o{ ACCOUNTS : origina
    ACCOUNTS ||--o{ TRANSACTIONS : contém
    CATEGORIES ||--o{ TRANSACTIONS : classifica
    CATEGORIES ||--o{ CATEGORY_RULES : gera
    CATEGORIES ||--o{ BUDGETS : referencia
    CATEGORIES ||--o{ CATEGORIES : subcategoria_de
    PLUGGY_ITEMS ||--o{ SYNC_LOGS : gera

    USERS {
        uuid id PK
        string email
        string password_hash
        string full_name
        timestamp created_at
    }
    PLUGGY_ITEMS {
        uuid id PK
        uuid user_id FK
        string pluggy_item_id
        string connector_name
        string status
        timestamp last_synced_at
    }
    ACCOUNTS {
        uuid id PK
        uuid user_id FK
        uuid pluggy_item_id FK
        string pluggy_account_id
        string type
        string subtype
        string name
        numeric balance
        jsonb credit_data
    }
    TRANSACTIONS {
        uuid id PK
        uuid account_id FK
        string pluggy_transaction_id
        string description
        numeric amount
        date date
        string type
        uuid category_id FK
        string category_source
        string status
    }
    CATEGORIES {
        uuid id PK
        uuid user_id FK
        string name
        string type
        uuid parent_category_id FK
        boolean is_system_default
    }
    CATEGORY_RULES {
        uuid id PK
        uuid category_id FK
        string match_type
        string match_value
        int priority
    }
    BUDGETS {
        uuid id PK
        uuid user_id FK
        uuid category_id FK
        numeric amount_limit
        date reference_month
    }
    GOALS {
        uuid id PK
        uuid user_id FK
        string name
        numeric target_amount
        numeric current_amount
        date target_date
        string status
    }
    BILLS {
        uuid id PK
        uuid user_id FK
        string name
        numeric amount
        int due_day
        string recurrence
        boolean is_paid
    }
    NOTIFICATIONS {
        uuid id PK
        uuid user_id FK
        string type
        string title
        boolean read
    }
    SYNC_LOGS {
        uuid id PK
        uuid pluggy_item_id FK
        string event_type
        string status
        timestamp created_at
    }
```

### 5.2 Especificação das tabelas

#### `users`
| Coluna | Tipo | Notas |
|---|---|---|
| id | uuid, PK | `gen_random_uuid()` |
| email | varchar(255), unique, not null | |
| password_hash | varchar(255), not null | Argon2id |
| full_name | varchar(150) | Usado na saudação do dashboard |
| created_at / updated_at | timestamptz | |

#### `pluggy_items`
| Coluna | Tipo | Notas |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK → users | |
| pluggy_item_id | varchar(64), unique, not null | ID retornado pela Pluggy |
| connector_id | int | |
| connector_name | varchar(100) | Ex.: "Banco Inter" |
| status | enum: `UPDATED`, `UPDATING`, `LOGIN_ERROR`, `WAITING_USER_INPUT`, `OUTDATED`, `ERROR` | Espelha `executionStatus`/`status` da Pluggy |
| last_synced_at | timestamptz, nullable | |
| created_at / updated_at | timestamptz | |

#### `accounts`
| Coluna | Tipo | Notas |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK | |
| pluggy_item_id | uuid, FK, nullable | Nulo = conta manual (ex.: dinheiro em espécie) |
| pluggy_account_id | varchar(64), nullable, unique quando presente | |
| type | enum: `BANK`, `CREDIT`, `MANUAL` | |
| subtype | varchar(50) | `CHECKING_ACCOUNT`, `SAVINGS_ACCOUNT`, `CREDIT_CARD`, `CASH` |
| name | varchar(150) | |
| balance | numeric(14,2) | |
| currency_code | varchar(3), default `BRL` | |
| credit_data | jsonb, nullable | `{limit, available_limit, due_date, minimum_payment, brand}` |
| created_at / updated_at | timestamptz | |

#### `transactions`
| Coluna | Tipo | Notas |
|---|---|---|
| id | uuid, PK | |
| account_id | uuid, FK | |
| pluggy_transaction_id | varchar(64), nullable | Único quando presente; nulo = transação manual |
| description | varchar(255) | Descrição tratada/normalizada |
| description_raw | varchar(255) | Como veio da Pluggy |
| amount | numeric(14,2) | Positivo = crédito, negativo = débito (convenção única) |
| currency_code | varchar(3) | |
| date | date | |
| type | enum: `DEBIT`, `CREDIT` | |
| category_id | uuid, FK, nullable | |
| category_source | enum: `PLUGGY`, `RULE`, `MANUAL`, `UNCATEGORIZED` | |
| merchant_name | varchar(150), nullable | |
| notes | text, nullable | Anotação livre do usuário |
| status | enum: `POSTED`, `PENDING` | |
| created_at / updated_at | timestamptz | |
| **Constraint** | `UNIQUE(account_id, pluggy_transaction_id)` | Garante idempotência de sync |

#### `categories`
| Coluna | Tipo | Notas |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK, nullable | Nulo = categoria padrão do sistema (seed) |
| name | varchar(80) | |
| icon | varchar(50) | Nome do ícone (lucide) |
| color | varchar(7) | Hex |
| parent_category_id | uuid, FK, nullable | Subcategorias |
| type | enum: `INCOME`, `EXPENSE` | |
| is_system_default | boolean | |

#### `category_rules`
| Coluna | Tipo | Notas |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK | |
| category_id | uuid, FK | |
| match_type | enum: `KEYWORD`, `MERCHANT_EXACT`, `REGEX` | |
| match_value | varchar(255) | |
| priority | int, default 100 | Menor = avaliado primeiro |

#### `budgets`
| Coluna | Tipo | Notas |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK | |
| category_id | uuid, FK, nullable | Nulo = orçamento geral do mês |
| amount_limit | numeric(14,2) | |
| reference_month | date | Sempre dia 1 do mês (ex.: `2026-09-01`) |
| **Constraint** | `UNIQUE(user_id, category_id, reference_month)` | |

#### `goals`
| Coluna | Tipo | Notas |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK | |
| name | varchar(120) | |
| target_amount | numeric(14,2) | |
| current_amount | numeric(14,2), default 0 | |
| target_date | date, nullable | |
| linked_account_id | uuid, FK, nullable | Ex.: vincular a uma poupança |
| status | enum: `IN_PROGRESS`, `COMPLETED`, `ARCHIVED` | |

#### `bills`
| Coluna | Tipo | Notas |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK | |
| name | varchar(120) | |
| amount | numeric(14,2), nullable | Nulo = valor variável |
| due_day | int, nullable | 1–31, para recorrência mensal |
| due_date | date, nullable | Para `ONE_TIME` |
| recurrence | enum: `MONTHLY`, `WEEKLY`, `YEARLY`, `ONE_TIME` | |
| category_id | uuid, FK, nullable | |
| is_paid | boolean, default false | Resetado automaticamente no novo ciclo |
| last_paid_at | timestamptz, nullable | |
| linked_transaction_id | uuid, FK, nullable | Preenchido quando o sistema identifica o pagamento por matching |
| reminder_days_before | int, default 3 | |

#### `notifications`
| Coluna | Tipo | Notas |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK | |
| type | enum: `BILL_DUE`, `BUDGET_EXCEEDED`, `SYNC_ERROR`, `GOAL_ACHIEVED` | |
| title / body | varchar / text | |
| read | boolean, default false | |
| metadata | jsonb, nullable | |
| created_at | timestamptz | |

#### `sync_logs`
| Coluna | Tipo | Notas |
|---|---|---|
| id | uuid, PK | |
| pluggy_item_id | uuid, FK | |
| event_type | varchar(50) | Nome do evento webhook ou `MANUAL_REFRESH`/`SCHEDULED_SYNC` |
| status | enum: `SUCCESS`, `ERROR` | |
| payload | jsonb | Corpo bruto recebido, para auditoria/depuração |
| error_message | text, nullable | |
| created_at | timestamptz | |

### 5.3 Índices recomendados
- `transactions(account_id, date DESC)` — listagem paginada por conta/período.
- `transactions(category_id)`
- `transactions(pluggy_transaction_id)` — já coberto pela constraint única.
- `accounts(user_id)`
- `budgets(user_id, reference_month)`
- `bills(user_id, due_day)`

---

## 6. Requisitos Funcionais (RF)

### 6.1 Autenticação e Sessão
- **RF-001**: O sistema deve permitir login com e-mail e senha, retornando `access_token` (JWT, curta duração) e `refresh_token` (longa duração).
- **RF-002**: O app deve renovar o `access_token` automaticamente usando o `refresh_token`, de forma transparente ao usuário (interceptor no Dio).
- **RF-003**: No Android, o app deve oferecer trava adicional por biometria ou PIN local antes de exibir dados, mesmo com sessão JWT válida.
- **RF-004**: O sistema deve permitir logout, invalidando o `refresh_token` no backend.
- **RF-005**: Deve existir um endpoint de criação/registro de usuário (usado uma única vez, na configuração inicial do sistema pelo próprio dono).

### 6.2 Conexão de Contas (Onboarding Pluggy)
- **RF-010**: O usuário deve conseguir iniciar o fluxo de conexão bancária a partir de uma tela de "Adicionar Conta".
- **RF-011**: O app deve exibir o widget **Pluggy Connect** (WebView no Android, fluxo de redirecionamento/nova aba na Web) para autorizar o Banco Inter via Open Finance.
- **RF-012**: Ao concluir a conexão com sucesso, o sistema deve persistir o `Item` e importar automaticamente todas as contas e o histórico de transações disponível.
- **RF-013**: O usuário deve poder ver o status de cada conexão (`Atualizado`, `Atualizando`, `Erro de login`, `Requer ação`) e forçar uma nova sincronização manual.
- **RF-014**: O usuário deve poder desconectar (remover) uma instituição, com confirmação explícita, mantendo o histórico de transações já importado (soft-delete da conexão, não das transações).

### 6.3 Dashboard
- **RF-020**: A tela inicial deve exibir saldo consolidado de todas as contas, saudação personalizada com o nome do usuário, gasto do mês corrente vs. orçamento total, e atalho para o extrato recente.
- **RF-021**: Deve haver indicador visual de contas a pagar próximas do vencimento.
- **RF-022**: Deve haver gráfico rápido de gasto por categoria do mês corrente.

### 6.4 Contas e Cartões
- **RF-030**: Listar todas as contas (bancárias, cartão de crédito, manuais) com saldo/fatura atual.
- **RF-031**: Detalhe de conta: extrato paginado, filtrável por período.
- **RF-032**: Detalhe de cartão de crédito: fatura atual, limite disponível, data de vencimento, valor mínimo (quando disponível na Pluggy).
- **RF-033**: Permitir criação de conta manual (ex.: "Dinheiro em espécie"), sem vínculo com Pluggy.
- **RF-034**: Permitir edição/exclusão de conta manual (contas sincronizadas via Pluggy não podem ser editadas/excluídas diretamente, apenas desconectadas — RF-014).

### 6.5 Transações
- **RF-040**: Listar transações com filtros por conta, categoria, tipo (débito/crédito), período e busca textual por descrição.
- **RF-041**: Permitir edição da categoria de uma transação, sobrescrevendo a categorização automática (`category_source` passa a `MANUAL`).
- **RF-042**: Permitir adicionar nota/observação livre a qualquer transação.
- **RF-043**: Permitir criação de transação manual (não vinda de sincronização), associada a uma conta manual ou como lançamento avulso.
- **RF-044**: Permitir exclusão apenas de transações manuais.
- **RF-045** *(diferencial)*: Permitir dividir uma transação em múltiplas categorias (ex.: uma compra de supermercado dividida entre "Alimentação" e "Higiene").

### 6.6 Categorização
- **RF-050**: Toda transação sincronizada recebe automaticamente a categoria enriquecida pela Pluggy como sugestão inicial (`category_source = PLUGGY`).
- **RF-051**: O sistema deve aplicar regras de categorização definidas pelo usuário (`category_rules`) por palavra-chave, nome de estabelecimento ou regex, com prioridade configurável, sobrepondo a categoria da Pluggy quando houver match (`category_source = RULE`).
- **RF-052**: O usuário deve poder criar, editar, remover e testar regras de categorização (pré-visualizar quantas transações passadas seriam afetadas).
- **RF-053**: O usuário deve poder criar categorias e subcategorias personalizadas, além das categorias padrão (seed inicial).

### 6.7 Orçamentos
- **RF-060**: Permitir definir um limite de gasto mensal por categoria.
- **RF-061**: Exibir progresso do orçamento (gasto atual / limite) com alerta visual ao ultrapassar 80% e 100%.
- **RF-062**: Gerar notificação (`BUDGET_EXCEEDED`) quando um orçamento for ultrapassado.
- **RF-063**: Permitir duplicar orçamentos do mês anterior para o mês corrente.

### 6.8 Metas Financeiras
- **RF-070**: Permitir criar metas com nome, valor-alvo e data-alvo opcional.
- **RF-071**: Permitir registrar aportes manuais a uma meta ou vinculá-la a uma conta (o saldo da conta vinculada atualiza `current_amount` automaticamente).
- **RF-072**: Notificar (`GOAL_ACHIEVED`) quando uma meta atingir 100%.

### 6.9 Contas a Pagar / Lembretes
- **RF-080**: Permitir cadastrar contas recorrentes (mensal, semanal, anual) ou pontuais, com valor (fixo ou variável), dia de vencimento e categoria.
- **RF-081**: O sistema deve gerar notificação (`BILL_DUE`) com antecedência configurável (`reminder_days_before`).
- **RF-082**: Permitir marcar manualmente uma conta como paga.
- **RF-083** *(diferencial)*: Tentar identificar automaticamente o pagamento de uma conta cadastrada ao encontrar uma transação sincronizada compatível (valor aproximado + categoria + janela de datas), sugerindo ao usuário a vinculação (`linked_transaction_id`).

### 6.10 Relatórios
- **RF-090**: Relatório de gasto por categoria em um período (gráfico de pizza/barras).
- **RF-091**: Relatório de fluxo de caixa (entradas vs. saídas) mês a mês.
- **RF-092**: Relatório de evolução patrimonial (soma de saldos ao longo do tempo).
- **RF-093**: Exportação dos dados (transações do período) em CSV. PDF como diferencial.

### 6.11 Notificações
- **RF-100**: Central de notificações in-app, listando alertas gerados (`BILL_DUE`, `BUDGET_EXCEEDED`, `SYNC_ERROR`, `GOAL_ACHIEVED`), com marcação de lidas/não lidas.
- **RF-101** *(Android)*: Notificações locais agendadas (`flutter_local_notifications`) para contas a pagar próximas, calculadas a partir do último dado sincronizado.

### 6.12 Configurações
- **RF-110**: Tela de perfil (nome, e-mail, troca de senha).
- **RF-111**: Gerenciamento de categorias e regras de categorização.
- **RF-112**: Gerenciamento de conexões Pluggy (ver RF-013/RF-014).
- **RF-113**: Exportação/backup completo dos dados do usuário (JSON ou CSV de todas as tabelas relevantes).

---

## 7. Integração com a Pluggy (Open Finance / Banco Inter)

### 7.1 Conceitos-chave e tokens

| Token | Onde vive | TTL | Uso |
|---|---|---|---|
| `CLIENT_ID` / `CLIENT_SECRET` | Variável de ambiente do backend | Permanente (rotacionável no dashboard) | Nunca usados diretamente em requisições de dados; servem só para gerar a `apiKey` |
| `apiKey` | Cache em memória do backend | 2 horas | Autentica **todas** as chamadas server-to-server à API da Pluggy (contas, transações, connect_token, webhooks) |
| `connectToken` | Gerado sob demanda pelo backend, entregue ao app | 30 minutos | Único token que o cliente Flutter recebe; autoriza apenas o widget Pluggy Connect e leitura restrita do item recém-criado |

**Regra de segurança inegociável:** `CLIENT_SECRET` e `apiKey` nunca trafegam para o app Flutter, em nenhuma circunstância — nem em modo debug.

### 7.2 Setup do projeto na Pluggy
1. Criar conta em `pluggy.ai` e uma Aplicação no Dashboard → obter `CLIENT_ID`/`CLIENT_SECRET` do ambiente **Sandbox** (desenvolvimento com dados simulados).
2. Desenvolver e testar todo o fluxo no Sandbox antes de tocar em dados reais.
3. Quando estiver pronto para uso real, seguir o fluxo **Meu Pluggy** (`meu.pluggy.ai`): o usuário conecta sua conta real do Inter lá, e depois vincula essa conexão à Aplicação criada no Dashboard — isso dá acesso real e gratuito, por tempo indeterminado, para uso pessoal.
4. Repetir o passo de vinculação no Meu Pluggy sempre que uma nova conta/instituição for conectada.

### 7.3 Fluxo de autenticação do backend
1. Rotina interna (`PluggyAuthService`) chama `POST /auth` com `CLIENT_ID`/`CLIENT_SECRET` e obtém `apiKey`.
2. `apiKey` fica em cache em memória com timestamp de expiração; toda chamada subsequente à Pluggy passa por um wrapper que verifica validade e renova proativamente ~10 minutos antes de expirar (ADR-004).
3. Falha de autenticação deve ser logada e reportada ao Sentry — é um erro crítico (nenhuma sincronização funciona sem `apiKey`).

### 7.4 Fluxo de conexão (Connect) — Android vs. Web

```mermaid
sequenceDiagram
    actor U as Usuário
    participant App as App Flutter
    participant BFF as Backend (FastAPI)
    participant Pluggy as Pluggy API

    U->>App: Toca em "Conectar conta"
    App->>BFF: POST /api/v1/pluggy/connect-token
    BFF->>Pluggy: POST /connect_token (usando apiKey)
    Pluggy-->>BFF: connectToken (30 min)
    BFF-->>App: connectToken

    alt Android
        App->>App: Abre WebView (flutter_inappwebview) carregando Pluggy Connect com o connectToken
    else Web
        App->>App: Abre Pluggy Connect em nova aba/iframe com connectToken + oauthRedirectUri apontando para o domínio do app
    end

    U->>Pluggy: Autoriza o Banco Inter (Open Finance, via app do próprio banco)
    Pluggy-->>App: callback onSuccess(itemId)
    App->>BFF: POST /api/v1/pluggy/items {item_id}
    BFF->>Pluggy: GET /items/{itemId} (usando apiKey)
    Pluggy-->>BFF: dados do Item
    BFF->>Pluggy: GET /accounts?itemId=...
    Pluggy-->>BFF: contas
    BFF->>Pluggy: GET /v2/transactions?accountId=... (cursor)
    Pluggy-->>BFF: transações
    BFF->>BFF: Persiste item, contas e transações; roda categorização automática
    BFF-->>App: 201 Created (resumo da conexão)
    App-->>U: Exibe contas conectadas
```

**Nota de implementação Web:** como o app Flutter Web roda inteiramente no navegador, o fluxo recomendado é abrir a URL hospedada do Pluggy Connect em uma nova aba/janela (`window.open` via `dart:html`/`url_launcher_web`), usando o parâmetro `oauthRedirectUri` apontando para uma rota do próprio app (ex.: `/connect/callback`). Essa rota, ao ser carregada, dispara uma checagem no backend (`GET /api/v1/pluggy/items?status=pending`) ou aguarda o webhook `item/created` já ter sido processado.

**Nota de implementação Android:** seguir o padrão do quickstart oficial da Pluggy para Flutter (`flutter_inappwebview`), carregando a mesma URL hospedada do Connect dentro da WebView e capturando os callbacks JS (`onSuccess`, `onError`, `onClose`) via `addJavaScriptHandler`.

### 7.5 Sincronização de dados

Estratégia em três camadas (redundância proposital, dado que dados financeiros não podem "sumir" silenciosamente):

1. **Webhook (tempo real)** — endpoint `POST /api/v1/webhooks/pluggy` recebe eventos:
   - `item/created`, `item/updated`, `item/error`, `item/waiting_user_input` (MFA pendente)
   - `transactions/created` → contém `createdTransactionsLink`; o backend pagina esse link e insere as transações novas.
   - `transactions/updated` → contém lista de `transactionIds`; o backend rebusca essas transações específicas e atualiza.
   - `transactions/deleted` → remove/marca como removida.
   - Toda mensagem tem um `eventId`. O backend deve registrar `eventId`s processados (tabela `sync_logs` ou índice único) para garantir **idempotência** em caso de reentrega.
2. **Sincronização manual** — usuário toca em "atualizar" (RF-013); backend chama `POST /items/{id}/update` (ou reconsulta diretamente contas/transações, dependendo do plano) e re-executa o pipeline de importação.
3. **Fallback agendado** — job do APScheduler roda a cada N horas (`[DECISÃO DO AGENTE]`, sugestão inicial: 6h) e verifica items cujo `last_synced_at` está muito antigo, forçando nova consulta — proteção contra falha silenciosa de webhook.

**Atenção (limitação documentada pela própria Pluggy):** transações vindas de conectores Open Finance regulado podem levar até 24h para ficarem disponíveis para consulta após ocorrerem no banco. Isso deve ser comunicado na UI (ex.: "dados podem levar até 24h para atualizar") para não parecer um bug do app.

### 7.6 Tratamento de erros
- Timeout/erro de rede da Pluggy → retry com backoff exponencial (máx. 3 tentativas), depois registrar `sync_logs.status = ERROR` e gerar notificação `SYNC_ERROR`.
- `item.status = LOGIN_ERROR` (ex.: usuário revogou consentimento no banco) → exibir claramente na tela de conexões, orientando reconexão.
- `item.status = WAITING_USER_INPUT` (MFA) → **fora do fluxo de leitura pós-conexão inicial**; tratar apenas durante o Connect (a própria widget já lida com MFA visualmente).
- Webhook recebido malformado ou sem `eventId` reconhecido → responder `400` e logar, nunca deixar exception não tratada derrubar o endpoint (que precisa responder rápido para a Pluggy não re-tentar em excesso).

### 7.7 Segurança do endpoint de webhook
Este é um endpoint público por natureza (a Pluggy precisa alcançá-lo pela internet). Mitigações obrigatórias:
- Validar, se disponível na versão atual da API/dashboard da Pluggy, cabeçalho de assinatura HMAC do payload (**o agente deve consultar a documentação oficial da Pluggy no momento da implementação para confirmar o mecanismo de assinatura vigente**, pois não há garantia documental estável sobre o formato exato do header).
- Como camada adicional independente disso, usar uma URL de webhook com um **token secreto embutido no path** (ex.: `/api/v1/webhooks/pluggy/{webhook_secret}`), comparado via `secrets.compare_digest` contra uma variável de ambiente — evita que qualquer requisição aleatória na internet seja processada mesmo sem confirmação de assinatura.
- Rate limiting no endpoint de webhook.
- Toda ação disparada por webhook deve ser idempotente (reprocessar o mesmo evento não deve duplicar dados), apoiada nas constraints únicas do schema (`pluggy_transaction_id`, `eventId`).

### 7.8 Endpoints da Pluggy utilizados (referência)
| Endpoint | Uso no finapp |
|---|---|
| `POST /auth` | Obter `apiKey` a partir de `CLIENT_ID`/`CLIENT_SECRET` |
| `POST /connect_token` | Gerar token de curta duração para o widget |
| `GET /connectors` | Listar conectores disponíveis (usado para restringir a widget só ao Inter, se desejado, via `selectedConnectorId`) |
| `GET /items/{id}` | Consultar status de uma conexão |
| `GET /accounts?itemId=` | Contas de um item |
| `GET /v2/transactions?accountId=` (cursor-based) | Transações paginadas |
| `POST /webhooks` | Registrar webhook da aplicação |
| `GET /webhooks` / `DELETE /webhooks/{id}` | Gerenciamento |

---

## 8. Design da API do BFF (REST, `/api/v1`)

Convenções gerais:
- Autenticação via header `Authorization: Bearer <access_token>` em todas as rotas exceto `/auth/login`, `/auth/register` (uso único) e `/webhooks/pluggy/{secret}`.
- Formato de erro padronizado (inspirado em RFC 7807):
```json
{
  "type": "https://finapp.dev/errors/validation-error",
  "title": "Erro de validação",
  "status": 422,
  "detail": "Um ou mais campos são inválidos",
  "errors": [{"field": "amount", "message": "Deve ser maior que zero"}]
}
```
- Paginação por `page`/`page_size` (default 20, máx. 100), resposta com envelope `{"items": [...], "total": N, "page": N, "page_size": N}`.
- Todas as datas em ISO-8601, valores monetários como string decimal (nunca float) para evitar erro de arredondamento.

### 8.1 Autenticação
| Método | Rota | Descrição |
|---|---|---|
| POST | `/auth/register` | Cria o usuário único (uso administrativo, protegido por variável `SETUP_TOKEN`) |
| POST | `/auth/login` | Retorna `access_token` + `refresh_token` |
| POST | `/auth/refresh` | Renova `access_token` |
| POST | `/auth/logout` | Invalida `refresh_token` |
| GET | `/auth/me` | Dados do usuário logado |

### 8.2 Pluggy
| Método | Rota | Descrição |
|---|---|---|
| POST | `/pluggy/connect-token` | Gera `connectToken` para o widget |
| POST | `/pluggy/items` | Confirma criação de item vindo do callback do cliente |
| GET | `/pluggy/items` | Lista conexões do usuário |
| DELETE | `/pluggy/items/{item_id}` | Desconecta uma instituição |
| POST | `/pluggy/items/{item_id}/sync` | Força sincronização manual |
| POST | `/webhooks/pluggy/{secret}` | Endpoint receptor de webhooks (ver 7.7) |

### 8.3 Contas
| Método | Rota | Descrição |
|---|---|---|
| GET | `/accounts` | Lista contas |
| GET | `/accounts/{id}` | Detalhe |
| POST | `/accounts` | Cria conta manual |
| PATCH | `/accounts/{id}` | Edita conta manual |
| DELETE | `/accounts/{id}` | Remove conta manual |

### 8.4 Transações
| Método | Rota | Descrição |
|---|---|---|
| GET | `/transactions` | Lista/filtra (`account_id`, `category_id`, `type`, `date_from`, `date_to`, `search`) |
| GET | `/transactions/{id}` | Detalhe |
| POST | `/transactions` | Cria transação manual |
| PATCH | `/transactions/{id}` | Edita categoria/nota |
| DELETE | `/transactions/{id}` | Remove (somente manuais) |
| POST | `/transactions/{id}/split` | Divide em múltiplas categorias (diferencial) |

### 8.5 Categorias e Regras
| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/categories` | Lista / cria |
| PATCH/DELETE | `/categories/{id}` | Edita / remove |
| GET/POST | `/categories/rules` | Lista / cria regras |
| PATCH/DELETE | `/categories/rules/{id}` | Edita / remove |
| POST | `/categories/rules/preview` | Simula impacto de uma regra em transações existentes |

### 8.6 Orçamentos
| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/budgets` | Lista / cria |
| PATCH/DELETE | `/budgets/{id}` | Edita / remove |
| GET | `/budgets/{id}/progress` | Progresso atual |
| POST | `/budgets/duplicate-previous-month` | RF-063 |

### 8.7 Metas
| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/goals` | Lista / cria |
| PATCH/DELETE | `/goals/{id}` | Edita / remove |
| POST | `/goals/{id}/contribute` | Registra aporte manual |

### 8.8 Contas a Pagar
| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/bills` | Lista / cria |
| PATCH/DELETE | `/bills/{id}` | Edita / remove |
| POST | `/bills/{id}/mark-paid` | Marca como pago |

### 8.9 Relatórios
| Método | Rota | Descrição |
|---|---|---|
| GET | `/reports/summary?month=` | Resumo do dashboard |
| GET | `/reports/category-breakdown?month=` | Gasto por categoria |
| GET | `/reports/cashflow?from=&to=` | Entradas vs. saídas |
| GET | `/reports/net-worth-history` | Evolução patrimonial |
| GET | `/reports/export?format=csv` | Exportação |

### 8.10 Notificações
| Método | Rota | Descrição |
|---|---|---|
| GET | `/notifications` | Lista |
| PATCH | `/notifications/{id}/read` | Marca como lida |

### 8.11 Saúde do sistema
| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Liveness (processo no ar) |
| GET | `/health/ready` | Readiness (checa conexão com DB e validade do cache de apiKey) |

---

## 9. Requisitos Não-Funcionais (RNF)

| ID | Categoria | Requisito |
|---|---|---|
| RNF-001 | Performance | Endpoints de CRUD devem responder em p95 < 300ms sob carga normal de uso pessoal (single-user, poucas dezenas de req/min no pico). |
| RNF-002 | Performance | Listagens de transações devem ser paginadas (máx. 100 itens por página) e usar índices adequados; nunca retornar tabela inteira sem paginação. |
| RNF-003 | Performance | Jobs de sincronização (webhook ou agendado) devem rodar como *background tasks* do FastAPI ou tarefas do APScheduler, nunca bloqueando a thread de resposta HTTP. |
| RNF-004 | Disponibilidade | Sistema de uso pessoal — não há SLA formal, mas o backend deve se recuperar automaticamente de reinícios (idempotência de sync, sem estado em memória crítico que não possa ser reconstruído). |
| RNF-005 | Confiabilidade | Nenhuma escrita financeira (transação, saldo) deve ocorrer sem estar dentro de uma transação de banco de dados (`BEGIN/COMMIT` via SQLAlchemy session). |
| RNF-006 | Segurança | Ver Seção 11 (dedicada). |
| RNF-007 | Observabilidade | Ver Seção 12 (dedicada). |
| RNF-008 | Manutenibilidade | Cobertura de testes mínima recomendada: 80% em `domain/` e `application/` do backend; 100% das regras de categorização e cálculo de orçamento/meta (lógica financeira crítica). |
| RNF-009 | Manutenibilidade | Código deve passar em `ruff check`, `ruff format --check` e `mypy --strict` no backend; `flutter analyze` sem warnings no frontend, como *gate* obrigatório de CI. |
| RNF-010 | Usabilidade | Todos os valores monetários exibidos em `pt_BR` (`R$ 1.234,56`); todas as datas em formato brasileiro. |
| RNF-011 | Acessibilidade | Contraste mínimo AA (WCAG) nas telas principais; todos os botões interativos com `Semantics`/labels acessíveis. |
| RNF-012 | Compatibilidade | Android: suportar `minSdkVersion` correspondente ao Flutter stable atual (verificar no momento do `flutter create`, tipicamente API 21+ ou a mínima suportada pelo canal stable vigente). Web: últimas duas versões estáveis de Chrome, Firefox e Edge. |
| RNF-013 | Portabilidade | Backend deve ser executável localmente via `docker-compose up` sem nenhuma dependência de serviço externo pago (Pluggy Sandbox cobre isso). |
| RNF-014 | Consistência de dados | Nenhum valor monetário deve ser representado como `float` no backend ou no app — sempre `Decimal`/`numeric` no Postgres e `String`/tipo decimal explícito no Dart. |

---

## 10. Segurança

### 10.1 Autenticação e autorização
- Senha do usuário: hash com **Argon2id** (`passlib`), nunca MD5/SHA puro.
- `access_token` JWT: expiração curta (15 min), assinado com `JWT_SECRET` (mínimo 256 bits, gerado aleatoriamente, nunca reaproveitado de exemplo).
- `refresh_token`: expiração longa (7–30 dias), armazenado hasheado no banco (tabela própria ou coluna em `users`), rotacionado a cada uso (refresh token rotation) para mitigar replay em caso de vazamento.
- Rate limiting (`slowapi`) obrigatório em `/auth/login` (ex.: 5 tentativas / 5 min por IP) para mitigar força bruta.
- Trava local no Android (RF-003) é uma camada de UX/segurança adicional, não substitui o JWT.

### 10.2 Armazenamento de tokens no cliente
- **Android**: `flutter_secure_storage`, que usa o Android Keystore por baixo dos panos.
- **Web**: **não usar `localStorage`/`sessionStorage`** para o `refresh_token` (vulnerável a XSS). Estratégia recomendada:
  - `access_token` mantido apenas em memória (estado Riverpod), nunca persistido em disco no navegador.
  - `refresh_token` entregue pelo backend como **cookie `HttpOnly`, `Secure`, `SameSite=Strict`**, de forma que o JavaScript do Flutter Web nunca tenha acesso direto a ele — o próprio navegador o reenvia automaticamente na chamada de `/auth/refresh`.
  - Isso implica que o backend deve diferenciar clientes Web (usa cookie) de clientes Android (usa corpo JSON) no fluxo de `/auth/refresh` — `[DECISÃO DO AGENTE]` implementar via header customizado (`X-Client-Platform: web|android`) enviado pelo app.

### 10.3 Backend
- Todas as variáveis sensíveis (`DATABASE_URL`, `JWT_SECRET`, `PLUGGY_CLIENT_ID`, `PLUGGY_CLIENT_SECRET`, `PLUGGY_WEBHOOK_SECRET`, `SENTRY_DSN`) somente via variáveis de ambiente/secrets da PaaS — nunca commitadas. `.env` no `.gitignore`; `.env.example` versionado com placeholders.
- HTTPS obrigatório — a própria PaaS (Railway/Render/Fly) provê TLS termination; backend deve recusar tráfego HTTP puro em produção (redirect 308 ou bloqueio).
- CORS restrito à(s) origem(ns) exata(s) do app Web em produção (nunca `*` fora de desenvolvimento local).
- Proteção contra SQL Injection: uso exclusivo do ORM parametrizado (SQLAlchemy) — proibido montar SQL via f-string/concatenção com dado de usuário.
- Headers de segurança HTTP (`Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`) via middleware.
- Dependências: `pip-audit` (backend) e `flutter pub outdated`/auditoria de pacotes (frontend) rodando no CI; Dependabot habilitado no GitHub.

### 10.4 Dados sensíveis
- O app **nunca** armazena nem manipula a senha/credenciais bancárias do usuário — o fluxo Open Finance via Pluggy Connect garante que essas credenciais nunca passam nem pelo backend nem pelo app (autorização acontece dentro do próprio app/site do banco).
- Dados financeiros (saldo, transações) são, por natureza, sensíveis (LGPD): mesmo em uso pessoal, seguir boas práticas de minimização — não logar valores de transação/saldo em texto claro nos logs de aplicação (logar apenas IDs).

### 10.5 Checklist de segurança antes de "produção real" (indo do Sandbox para Meu Pluggy)
1. Segredos rotacionados e diferentes dos usados em desenvolvimento.
2. `DEBUG=False` e documentação interativa (`/docs`, `/redoc`) desabilitada ou protegida por autenticação básica adicional em produção.
3. Backup automático do PostgreSQL habilitado na PaaS.
4. Sentry configurado e testado (disparar um erro proposital e confirmar recebimento).
5. Webhook secret configurado e testado.

---

## 11. Observabilidade

- **Logging estruturado** (`structlog`, formato JSON): todo log deve incluir `request_id` (gerado por middleware, propagado via `contextvars`), `user_id` (quando autenticado), `event` e `level`. Nunca logar segredos ou valores monetários brutos além do necessário.
- **Rastreamento de erros**: Sentry integrado no backend (exceptions não tratadas, falhas de sincronização Pluggy) e, como diferencial, no app Flutter (`sentry_flutter`).
- **Health checks**: `/health` (liveness) e `/health/ready` (readiness, valida conexão com Postgres e presença de `apiKey` válida em cache).
- **Auditoria de sincronização**: tabela `sync_logs` funciona como trilha de auditoria simplificada de tudo que a Pluggy notificou/foi consultado — deve ser consultável (mesmo que só via query direta/admin simples) para depuração de "por que essa transação não apareceu".
- **Métricas** *(diferencial, não obrigatório)*: expor `/metrics` no formato Prometheus (`prometheus-fastapi-instrumentator`) caso o usuário queira, no futuro, plugar um Grafana Cloud gratuito.

---

## 12. Estratégia de Testes

### 12.1 Backend
| Tipo | Ferramenta | Escopo |
|---|---|---|
| Unitário | `pytest` | `domain/` (entidades, regras de categorização, cálculo de progresso de orçamento/meta) e `application/` (use cases), com repositórios mockados |
| Integração | `pytest` + banco de testes (Postgres efêmero via `docker-compose.test.yml` ou `testcontainers-python`) | Repositórios reais, migrations aplicadas, fluxo completo de um use case |
| Contrato/Mock externo | `respx` | Simula respostas da API da Pluggy (sucesso, erro, timeout, payloads de webhook reais documentados na Seção 15) |
| API (end-to-end do backend) | `httpx.AsyncClient` contra a app FastAPI in-process | Principais fluxos: login → conectar item (mockado) → listar transações → criar orçamento → progresso |

Todas as regras de negócio financeiras (categorização automática, cálculo de progresso de orçamento, detecção de conta paga) devem ter testes cobrindo casos de borda (valores negativos, mês sem dados, categoria removida, transação duplicada por reenvio de webhook).

### 12.2 Frontend (Flutter)
| Tipo | Ferramenta | Escopo |
|---|---|---|
| Unitário | `flutter_test` + `mocktail` | Providers Riverpod (lógica de estado), formatação de moeda/data, parsing de DTOs |
| Widget | `flutter_test` | Componentes isolados (card de conta, item de transação, gráfico) |
| Integração | `integration_test` | Fluxos críticos: login → conectar conta (com backend mockado) → ver extrato → criar orçamento |
| Golden *(diferencial)* | `golden_toolkit` | Snapshots visuais de telas-chave para evitar regressão de UI |

### 12.3 Definição de "pronto" para testes
Nenhuma funcionalidade da Seção 6 é considerada concluída sem: (a) teste unitário da regra de negócio associada, (b) teste de integração do endpoint correspondente, (c) tratamento explícito de pelo menos um caso de erro.

---

## 13. CI/CD e Ambientes

### 13.1 Pipelines (GitHub Actions)

**`backend-ci.yml`** (trigger: PR e push em `backend/**`):
1. Setup Python + cache de dependências.
2. `ruff check` + `ruff format --check` + `mypy`.
3. Subir Postgres de teste (serviço do GitHub Actions).
4. Rodar `alembic upgrade head` no banco de teste.
5. `pytest --cov` com limite mínimo de cobertura (falha o build abaixo do threshold definido em RNF-008).
6. Build da imagem Docker (sem push, só valida que builda).

**`backend-deploy.yml`** (trigger: push em `main`):
1. Repete os checks acima.
2. Build e push da imagem/deploy automático na PaaS escolhida (Railway/Render/Fly — configurar via CLI/GitHub integration nativa da plataforma).
3. Roda `alembic upgrade head` contra o banco de produção como etapa de release (release command da PaaS).

**`app-ci.yml`** (trigger: PR e push em `app/**`):
1. Setup Flutter (versão fixada em arquivo `.flutter-version` ou similar).
2. `flutter pub get` + `build_runner build` (geração de freezed/riverpod).
3. `flutter analyze`.
4. `flutter test --coverage`.
5. Build de verificação: `flutter build apk --debug` e `flutter build web`.

**`app-release.yml`** (trigger manual/tag):
1. Build `flutter build apk --release` (assinado com keystore armazenado em secret do GitHub) e `flutter build web --release`.
2. Publica os artefatos (APK como release do GitHub; build web enviado à hospedagem estática escolhida).

### 13.2 Ambientes
| Ambiente | Backend | Pluggy | Banco |
|---|---|---|---|
| Local (dev) | `docker-compose up` | Sandbox | Postgres em container local |
| Produção (uso real) | PaaS (Railway/Render/Fly) | Meu Pluggy | Postgres gerenciado da PaaS |

Não há ambiente de "staging" formal dado tratar-se de projeto pessoal — testes de integração cobrem essa lacuna antes do deploy.

---

## 14. Estrutura de Pastas dos Repositórios

### 14.1 Backend (`/backend`)

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py            # Settings via pydantic-settings, lê variáveis de ambiente
│   │   ├── security.py          # Hash de senha, criação/validação de JWT
│   │   ├── logging.py           # Configuração do structlog
│   │   └── exceptions.py        # Exceções de domínio + handlers globais do FastAPI
│   ├── domain/
│   │   ├── entities/             # Entidades puras (dataclasses), ex: Transaction, Budget
│   │   ├── value_objects/        # Ex: Money, DateRange
│   │   ├── repositories/         # Interfaces (Protocol/ABC) — ex: TransactionRepository
│   │   └── services/             # Regras puras: CategorizationEngine, BudgetProgressCalculator
│   ├── application/
│   │   ├── use_cases/
│   │   │   ├── auth/
│   │   │   ├── accounts/
│   │   │   ├── transactions/
│   │   │   ├── categories/
│   │   │   ├── budgets/
│   │   │   ├── goals/
│   │   │   ├── bills/
│   │   │   └── pluggy_sync/
│   │   └── dto/                  # DTOs internos entre camadas (não confundir com schemas HTTP)
│   ├── infrastructure/
│   │   ├── db/
│   │   │   ├── models/           # Modelos SQLAlchemy (ORM)
│   │   │   ├── repositories/     # Implementações concretas das interfaces de domain/repositories
│   │   │   └── session.py        # Engine/sessionmaker assíncronos
│   │   ├── pluggy/
│   │   │   ├── client.py         # Wrapper httpx da API Pluggy (auth, connect_token, accounts, transactions)
│   │   │   ├── webhook_handler.py
│   │   │   └── schemas.py        # Modelos Pydantic dos payloads da Pluggy
│   │   ├── cache/
│   │   │   └── memory_token_cache.py   # Implementa a interface PluggyTokenCache (ADR-004)
│   │   └── scheduler/
│   │       └── jobs.py           # Jobs do APScheduler (sync fallback, verificação de bills)
│   └── presentation/
│       ├── api/
│       │   └── v1/
│       │       ├── routers/      # auth.py, accounts.py, transactions.py, categories.py, budgets.py,
│       │       │                 # goals.py, bills.py, pluggy.py, reports.py, notifications.py, health.py
│       │       └── schemas/      # Pydantic request/response por recurso
│       ├── dependencies.py       # Depends(): sessão de DB, usuário autenticado, repositórios injetados
│       └── main.py               # Instancia FastAPI, registra routers, middlewares, startup/shutdown
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/                 # Payloads de exemplo da Pluggy (ver Seção 18)
│   └── conftest.py
├── Dockerfile
├── docker-compose.yml            # api + postgres, para dev local
├── docker-compose.test.yml       # postgres efêmero para testes de integração
├── pyproject.toml
├── .env.example
└── README.md
```

### 14.2 Frontend (`/app`)

```
app/
├── lib/
│   ├── core/
│   │   ├── constants/
│   │   ├── theme/                 # Design tokens, cores, tipografia
│   │   ├── router/                 # go_router: rotas + guards de autenticação
│   │   ├── network/                 # Dio client, interceptors (auth, logging, refresh)
│   │   ├── storage/                  # Wrapper de secure storage (Android) / estratégia Web (Seção 10.2)
│   │   ├── errors/                    # Failure types, mapeamento de erros da API
│   │   └── utils/                      # Formatação de moeda/data (intl)
│   ├── features/
│   │   ├── auth/
│   │   │   ├── data/
│   │   │   ├── domain/
│   │   │   └── presentation/
│   │   ├── onboarding_connect/         # Fluxo de conexão Pluggy (WebView/redirect)
│   │   ├── dashboard/
│   │   ├── accounts/
│   │   ├── transactions/
│   │   ├── categories/
│   │   ├── budgets/
│   │   ├── goals/
│   │   ├── bills/
│   │   ├── reports/
│   │   ├── notifications/
│   │   └── settings/
│   ├── shared/
│   │   └── widgets/                    # Componentes reutilizáveis (cards, charts wrappers, etc.)
│   ├── app.dart                        # MaterialApp.router, tema, providers globais
│   └── main.dart
├── test/
├── integration_test/
├── analysis_options.yaml
├── pubspec.yaml
└── README.md
```

---

## 15. Categorização Automática de Transações

Abordagem em **cascata determinística** (sem dependência de serviço de IA externo na v1 — mantendo simplicidade e custo zero, conforme premissa de uso pessoal):

```mermaid
flowchart TD
    A[Nova transação sincronizada] --> B{Existe regra do usuário<br/>com match?}
    B -- Sim, maior prioridade --> C[category_source = RULE]
    B -- Não --> D{Pluggy retornou<br/>categoria enriquecida?}
    D -- Sim --> E[category_source = PLUGGY]
    D -- Não --> F[category_source = UNCATEGORIZED]
    C --> G[Transação salva]
    E --> G
    F --> G
    G --> H[Usuário pode sobrescrever manualmente<br/>a qualquer momento → category_source = MANUAL]
```

- O `CategorizationEngine` vive em `domain/services/` (regra pura, testável sem banco): recebe a transação + lista de regras ativas do usuário e retorna a categoria sugerida e a origem.
- Regras (`category_rules`) são avaliadas em ordem de `priority` (menor primeiro); a primeira que der match vence.
- Tipos de match: `KEYWORD` (substring case-insensitive na descrição), `MERCHANT_EXACT` (igualdade com `merchant_name`), `REGEX` (expressão regular sobre a descrição).
- **Evolução futura (fora do escopo desta versão, registrar como item de roadmap):** plugar um classificador via LLM (ex.: API da Anthropic) para sugerir categoria em transações que caiam em `UNCATEGORIZED`, e/ou um assistente conversacional para perguntas em linguagem natural sobre os gastos ("quanto gastei em mercado esse mês?"). Isso deve ser implementado como uma nova implementação da mesma interface de categorização (Strategy Pattern), sem alterar o restante do sistema.

---

## 16. Notificações e Lembretes

- Toda notificação é primeiro um registro na tabela `notifications`, gerado por regras de domínio rodando após sync (orçamento estourado, meta atingida, erro de sync) ou pelo job agendado de verificação de contas a pagar (lembrete por proximidade de vencimento).
- O app consome `GET /notifications` para popular um ícone de sino com contador de não lidas — funciona igualmente em Android e Web, sem depender de infraestrutura de push.
- **Android (adicional, RF-101):** ao sincronizar dados de `bills`, o app agenda notificações locais (`flutter_local_notifications`) para os próximos vencimentos conhecidos. Isso cobre o caso de o usuário não abrir o app diariamente, sem exigir Firebase Cloud Messaging/push server-side.
- **Web:** sem notificações locais (limitação de navegador sem service worker de push configurado); o usuário vê os alertas ao abrir o app. Push Web via FCM é um possível diferencial futuro, não obrigatório.

---

## 17. Roadmap de Implementação (Fases)

Ordem sugerida de execução pelo agente de programação — cada fase deve terminar com testes passando e, quando aplicável, endpoints documentados no Swagger antes de avançar.

| Fase | Entregável |
|---|---|
| **0** | Setup do monorepo, `docker-compose` local, esqueleto FastAPI + esqueleto Flutter, configuração de lint/format/CI básico. |
| **1** | Backend: config, conexão com banco, modelos + migrations iniciais (`users`), autenticação (register/login/refresh/logout), testes de auth. |
| **2** | Backend: `PluggyClient` (auth, connect_token), endpoint `/pluggy/connect-token`, endpoint receptor de webhook (com validação de secret), testes com Pluggy mockada via `respx`, integração validada contra o **Sandbox** real da Pluggy. |
| **3** | Backend: modelos e endpoints de `accounts` e `transactions`, pipeline de importação pós-conexão (contas + histórico), `CategorizationEngine` (regras + categoria Pluggy), testes. |
| **4** | Backend: `categories`, `category_rules`, `budgets` (+ cálculo de progresso), `goals`, `bills` (+ job de lembrete), `notifications`. |
| **5** | Backend: endpoints de `reports` (summary, category-breakdown, cashflow, net-worth-history) e exportação CSV. Observabilidade (structlog, Sentry, health checks) consolidada. |
| **6** | Frontend: fundação do app (tema, router, cliente Dio + interceptors, estratégia de storage por plataforma), telas de login/registro, trava biométrica Android. |
| **7** | Frontend: fluxo de onboarding/conexão Pluggy (WebView Android + fluxo Web), tela de gerenciamento de conexões. |
| **8** | Frontend: dashboard, listagem/detalhe de contas, listagem/detalhe/edição de transações, gerenciamento de categorias e regras. |
| **9** | Frontend: orçamentos, metas, contas a pagar/lembretes, central de notificações. |
| **10** | Frontend: relatórios com gráficos (`fl_chart`), exportação, configurações/perfil. |
| **11** | Testes de integração end-to-end (backend `httpx` + Flutter `integration_test`), revisão de acessibilidade, polimento visual. |
| **12** | Migração de Sandbox → Meu Pluggy real, checklist de segurança de produção (Seção 10.5), deploy final na PaaS escolhida, monitoramento ativo por alguns dias antes de considerar "estável". |

---

## 18. Critérios de Aceite (exemplos representativos por módulo)

**Conexão de conta (RF-010 a RF-014)**
- Dado que o usuário toca em "Conectar conta", quando ele autoriza o Banco Inter com sucesso no widget, então o app deve exibir a nova conta na lista em até alguns segundos, com saldo importado.
- Dado um item com `status = LOGIN_ERROR`, quando o usuário abre a tela de conexões, então deve ver um indicativo visual de erro e uma ação clara de "reconectar".

**Sincronização (RF-050/RF-051, Seção 7.5)**
- Dado um webhook `transactions/created` reenviado duas vezes com o mesmo `eventId`/mesmas transações, quando processado, então nenhuma transação duplicada deve ser criada (garantido pela constraint única de `pluggy_transaction_id`).

**Orçamento (RF-060 a RF-062)**
- Dado um orçamento de R$ 500 para "Alimentação" no mês corrente, quando o total de transações da categoria no mês ultrapassa R$ 500, então uma notificação `BUDGET_EXCEEDED` deve ser criada uma única vez por mês/categoria (não repetir a cada nova transação).

**Contas a pagar (RF-080 a RF-083)**
- Dado uma conta recorrente mensal com vencimento no dia 10 e `reminder_days_before = 3`, quando faltarem 3 dias para o vencimento e ela ainda não estiver marcada como paga, então uma notificação `BILL_DUE` deve existir.

**Segurança de token (Seção 10.2)**
- Dado um usuário logado na versão Web, quando inspecionado o armazenamento do navegador (Local Storage/Session Storage), então nenhum token de autenticação deve estar presente em texto plano.

---

## 19. Variáveis de Ambiente

### 19.1 Backend (`.env.example`)
```env
# App
ENV=development                 # development | production
DEBUG=true
SETUP_TOKEN=change-me           # protege o endpoint de registro de usuário único

# Banco de dados
DATABASE_URL=postgresql+asyncpg://finapp:finapp@localhost:5432/finapp

# Autenticação
JWT_SECRET=change-me-to-a-random-256-bit-value
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Pluggy
PLUGGY_CLIENT_ID=
PLUGGY_CLIENT_SECRET=
PLUGGY_BASE_URL=https://api.pluggy.ai
PLUGGY_WEBHOOK_SECRET=change-me   # usado no path do endpoint de webhook, ver 7.7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:PORT_DO_APP_WEB

# Observabilidade
SENTRY_DSN=
LOG_LEVEL=INFO
```

### 19.2 Frontend (build-time config)
```env
API_BASE_URL=http://localhost:8000/api/v1
ENV=development
```
> No Flutter, usar `--dart-define` ou um pacote de config (ex.: `flutter_dotenv` apenas para dev local, nunca para segredo real — o app não guarda segredo nenhum, só a URL do backend).

---

## 20. Entregáveis e Documentação Esperada

- Código-fonte completo em monorepo Git, com histórico de commits significativo (não um único commit final).
- `README.md` raiz explicando o propósito do projeto e como navegar entre `/backend` e `/app`.
- `README.md` específico do backend: como rodar localmente (`docker-compose up`), como rodar migrations, como rodar testes, como configurar Pluggy Sandbox.
- `README.md` específico do app: como rodar (`flutter run -d chrome` / `flutter run -d <device-android>`), como gerar código (`build_runner`), como rodar testes.
- Documentação OpenAPI/Swagger gerada automaticamente pelo FastAPI (`/docs`), sempre atualizada por construção.
- Documento curto de "Guia de configuração da Pluggy" (setup de aplicação, Sandbox → Meu Pluggy), complementando a Seção 7.2 deste PRD.
- `.env.example` completo e atualizado (Seção 19).

---

## 21. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Mudança de senha/token do Inter revoga o consentimento Open Finance | Sincronização para de funcionar | Detectar `status = LOGIN_ERROR` e notificar claramente o usuário para reconectar (RF-013) |
| Latência de até 24h em transações de conectores Open Finance regulado | Usuário pode achar que o app "não atualiza" | Comunicar essa limitação na UI (tooltip/texto explicativo na tela de extrato) |
| Mudança na API/contratos da Pluggy (breaking changes) | Quebra de sincronização | Isolar toda comunicação em `infrastructure/pluggy/` (Adapter Pattern) — mudanças ficam contidas em um único módulo; testes de contrato (`respx`) pegam regressões |
| Dependência de terceiro único (Pluggy) para todo o core do produto | Indisponibilidade da Pluggy paralisa sync | Fora do controle do projeto; mitigar exibindo dados já armazenados localmente mesmo com Pluggy fora do ar (o app deve sempre funcionar em modo leitura sobre o último dado sincronizado) |
| Cache de `apiKey` em memória se perde a cada deploy/restart | Pequeno atraso até nova autenticação | Renovação automática e transparente na primeira chamada que falhar por token expirado (retry com nova autenticação) |
| Uso pessoal pode levar a menor rigor de testes ao longo do tempo | Dívida técnica silenciosa | Gate de CI obrigatório (Seção 13) impede merge sem lint/testes passando, independentemente da "pressa" do momento |

---

## 22. Anexos — Exemplos de Payloads da Pluggy

**Webhook `transactions/created`:**
```json
{
  "itemId": "de7bbf5a-abf2-47e4-94b1-586b36758423",
  "event": "transactions/created",
  "id": "de7bbf5a-abf2-47e4-94b1-586b36758423",
  "eventId": "4e69d62d-b7c8-4f01-b591-a1d8a94710b9",
  "accountId": "0d5a0de2-9c82-4ea2-af50-31643a632a33",
  "transactionsCreatedAtFrom": "2026-09-01T12:00:00.000Z",
  "createdTransactionsLink": "https://api.pluggy.ai/transactions?accountId=0d5a0de2-9c82-4ea2-af50-31643a632a33&createdAtFrom=2026-09-01T12:00:00.000Z"
}
```

**Webhook `transactions/updated`:**
```json
{
  "event": "transactions/updated",
  "eventId": "d876fd7c-e9bd-4c4c-bd46-cc96c62aac29",
  "itemId": "a5c763cb-0952-457b-9936-630f79c5b016",
  "accountId": "8a6e2c17-2817-40bb-b03d-546febc6a60a",
  "transactionIds": ["5a14feae-eaa7-423a-820c-6b83837c35b7"]
}
```

**Webhook `item/updated`:**
```json
{
  "event": "item/updated",
  "id": "a5c763cb-0952-457b-9936-630f79c5b016",
  "itemId": "a5c763cb-0952-457b-9936-630f79c5b016",
  "triggeredBy": "USER"
}
```

> Estes payloads foram obtidos da documentação pública oficial da Pluggy (docs.pluggy.ai) e servem de base para os fixtures de teste em `backend/tests/fixtures/`. O agente de programação deve validar o formato atual diretamente na documentação oficial antes de implementar, pois APIs de terceiros evoluem.

---

*Fim do documento.*
