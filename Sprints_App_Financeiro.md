# Backlog de Sprints — finapp

**Documento complementar ao `PRD_App_Financeiro.md`.** Este documento traduz todos os requisitos funcionais (RF), não-funcionais (RNF) e tarefas técnicas do PRD em um backlog executável, dividido em sprints sequenciais com subtasks.

## Como usar este documento

- Cada **Sprint** representa um incremento vertical: ao final dela, algo testável e demonstrável deve existir (nunca "só metade de uma feature").
- Sprints não têm duração fixa em dias — como é projeto solo, o tamanho real depende do ritmo do desenvolvedor/agente. Foi incluída uma coluna de **complexidade relativa** (P/M/G) apenas como guia de esforço.
- Toda subtask referencia o requisito de origem no PRD (`RF-XXX`, `RNF-XXX`, `ADR-XXX`, ou nº de seção) para rastreabilidade.
- Checkboxes (`- [ ]`) podem ser marcados conforme o progresso avança.
- **Definition of Done (DoD) padrão de toda sprint**, além do DoD específico listado: (1) testes unitários/integração da lógica nova passando; (2) `ruff`/`mypy` (backend) ou `flutter analyze` (frontend) sem erros; (3) endpoint novo documentado automaticamente no Swagger (`/docs`) — backend; (4) sem segredo hardcoded.
- A ordem segue o Roadmap da Seção 17 do PRD (backend completo → depois frontend). O **Sprint 9** (fundação Flutter) é puramente estrutural/sem dependência de backend pronto e **pode ser adiantado em paralelo** a qualquer momento a partir do Sprint 1, se o ritmo de trabalho permitir duas frentes.

## Visão geral das sprints

| # | Sprint | Foco | Complexidade | RFs / Seções cobertos |
|---|---|---|---|---|
| 0 | Fundação do Monorepo | Setup de projeto | P | Seções 3, 4, 13, 14 |
| 1 | Core Backend: Config, DB, Auth | Backend | M | RF-001 a RF-005 |
| 2 | Pluggy: Autenticação e Connect | Backend | M | RF-010, RF-011, Seção 7.2–7.3 |
| 3 | Contas e Importação Inicial | Backend | M | RF-012, RF-030 a RF-034 |
| 4 | Transações e Sincronização | Backend | G | RF-013, RF-040 a RF-045, Seção 7.5–7.6 |
| 5 | Categorização Automática | Backend | M | RF-050 a RF-053, Seção 15 |
| 6 | Orçamentos e Metas | Backend | M | RF-060 a RF-072 |
| 7 | Contas a Pagar e Notificações | Backend | M | RF-080 a RF-083, RF-100/101, RF-014 |
| 8 | Relatórios, Exportação e Observabilidade | Backend | M | RF-090 a RF-093, Seções 11 e 13 |
| 9 | Fundação do App Flutter | Frontend | M | Seções 4.2, 14.2 |
| 10 | Autenticação e Trava Local | Frontend | P | RF-001 a RF-004 |
| 11 | Onboarding e Conexão Pluggy | Frontend | G | RF-010 a RF-014 |
| 12 | Dashboard, Contas e Transações | Frontend | G | RF-020 a RF-022, RF-030 a RF-034, RF-040 a RF-045 |
| 13 | Categorias, Orçamentos, Metas, Contas a Pagar | Frontend | G | RF-052/053, RF-060 a RF-072, RF-080 a RF-083 |
| 14 | Relatórios, Notificações, Configurações | Frontend | M | RF-090 a RF-093, RF-100, RF-110 a RF-113 |
| 15 | Testes E2E, Acessibilidade e Polimento | Full-stack | M | Seção 12, RNF-011 |
| 16 | Produção: Segurança, Meu Pluggy e Deploy | DevOps | M | Seção 10.5, Seção 13.2, Fase 12 |

---

## Sprint 0 — Fundação do Monorepo

**Objetivo:** ter um esqueleto de projeto rodando localmente (mesmo sem funcionalidade real), com lint/CI/Docker configurados desde o primeiro commit.

**Subtasks**
- [x] Criar repositório Git único com pastas raiz `/backend` e `/app` (ADR-006 — monorepo)
- [x] Backend: inicializar `pyproject.toml` (via `uv` ou Poetry), configurar `ruff` (lint+format) e `mypy`
- [x] Backend: criar esqueleto FastAPI mínimo (`app/presentation/main.py`) com endpoint `GET /health` respondendo `200`
- [x] Backend: `Dockerfile` multi-stage (`python:3.12-slim`) e `docker-compose.yml` (serviço `api` + `postgres`)
- [x] Backend: `docker-compose.test.yml` com Postgres efêmero para testes de integração (usado a partir do Sprint 1)
- [x] Frontend: `flutter create` do projeto `app`, configurado para Android + Web (`flutter config --enable-web` se necessário)
- [x] Frontend: `analysis_options.yaml` estendendo `very_good_analysis` ou `flutter_lints`
- [x] Frontend: criar estrutura de pastas vazia conforme Seção 14.2 do PRD (`core/`, `features/`, `shared/`)
- [x] CI: `backend-ci.yml` rodando `ruff check` + `mypy` + build da imagem Docker (ainda sem testes reais)
- [x] CI: `app-ci.yml` rodando `flutter analyze` (ainda sem testes reais)
- [x] `README.md` raiz explicando a estrutura do monorepo e como rodar cada parte
- [x] `.env.example` inicial no backend (esqueleto, será completado ao longo das sprints)
- [x] Criar conta na Pluggy e uma Aplicação no Dashboard em modo **Sandbox**; guardar `CLIENT_ID`/`CLIENT_SECRET` de desenvolvimento (Seção 7.2, passo 1–2)

**DoD específico:** `docker-compose up` sobe a API respondendo em `/health`; `flutter run -d chrome` abre uma tela em branco sem erros; ambos os pipelines de CI passam (verdes) em um PR de teste.

---

## Sprint 1 — Core Backend: Config, Banco de Dados e Autenticação

**Objetivo:** usuário único consegue se autenticar de ponta a ponta com segurança de produção.

**Subtasks**
- [x] `core/config.py` com `pydantic-settings`, lendo todas as variáveis já previstas na Seção 19.1 (mesmo as que só serão usadas em sprints futuras — evita retrabalho)
- [x] `infrastructure/db/session.py`: engine assíncrono (`asyncpg`) + `sessionmaker`
- [x] Inicializar Alembic (`alembic init`), configurar `env.py` para rodar migrations assíncronas
- [x] Modelo ORM `User` + migration inicial (tabela `users`, Seção 5.2)
- [x] `domain/entities/user.py` (entidade pura) + `domain/repositories/user_repository.py` (interface)
- [x] `infrastructure/db/repositories/user_repository.py` (implementação concreta)
- [x] `core/security.py`: hash de senha (Argon2id via `passlib`), criação/validação de JWT (access + refresh)
- [x] Use case + endpoint `POST /auth/register` (RF-005), protegido por `SETUP_TOKEN`
- [x] Use case + endpoint `POST /auth/login` (RF-001)
- [x] Refresh token: armazenamento hasheado + rotação a cada uso (Seção 10.1) — coluna/tabela dedicada
- [x] Use case + endpoint `POST /auth/refresh` (RF-002)
- [x] Use case + endpoint `POST /auth/logout` (RF-004) — invalida refresh token
- [x] Endpoint `GET /auth/me`
- [x] Rate limiting em `/auth/login` via `slowapi` (Seção 10.1)
- [x] Middleware de `request_id` + `structlog` configurado (Seção 11) — usado a partir daqui em todos os logs
- [x] Exception handlers globais + formato de erro padronizado (Seção 8, formato RFC 7807-like)
- [x] Testes unitários: hashing de senha, criação/validação de JWT, expiração
- [x] Testes de integração: fluxo completo `register → login → me → refresh → logout` contra Postgres de teste

**DoD específico:** um usuário criado via `/auth/register` consegue logar, acessar `/auth/me`, renovar o token e fazer logout — tudo coberto por teste de integração automatizado.

---

## Sprint 2 — Integração Pluggy: Autenticação e Fluxo de Connect

**Objetivo:** o backend consegue autenticar-se na Pluggy e emitir tokens de conexão para o futuro cliente.

**Subtasks**
- [ ] `infrastructure/pluggy/client.py`: método de autenticação (`POST /auth` da Pluggy) usando `CLIENT_ID`/`CLIENT_SECRET`
- [ ] `infrastructure/cache/memory_token_cache.py`: cache em memória do `apiKey` com expiração e renovação proativa (~10 min antes de expirar) — implementa interface abstrata (ADR-004)
- [ ] `infrastructure/pluggy/schemas.py`: modelos Pydantic dos payloads relevantes (auth, connect_token, item)
- [ ] Método `PluggyClient.create_connect_token()` (`POST /connect_token`)
- [ ] Use case + endpoint `POST /pluggy/connect-token` (RF-010)
- [ ] Modelo ORM `PluggyItem` + migration (tabela `pluggy_items`, Seção 5.2)
- [ ] `domain/repositories/pluggy_item_repository.py` + implementação
- [ ] Use case + endpoint `POST /pluggy/items` — recebe `item_id` do cliente e persiste o registro inicial (RF-011/012, primeira metade)
- [ ] Endpoint receptor de webhook `POST /webhooks/pluggy/{secret}` — **esqueleto**: valida o secret no path (Seção 7.7), loga o payload recebido em `sync_logs` (criar essa tabela já aqui, mesmo que o processamento completo só venha no Sprint 4), responde `200` rapidamente
- [ ] Registrar a URL de webhook na Aplicação Pluggy (via Dashboard ou `POST /webhooks`)
- [ ] Testes unitários: cache de token (expiração, renovação)
- [ ] Testes de integração com `respx` mockando `/auth` e `/connect_token` da Pluggy
- [ ] Validação manual ponta a ponta contra o **Sandbox real** da Pluggy (gerar um `connectToken` de verdade via `curl`/Postman e confirmar que funciona)

**DoD específico:** `POST /pluggy/connect-token` autenticado retorna um `connectToken` válido gerado a partir de uma chamada real ao Sandbox da Pluggy; o endpoint de webhook responde `200` a um evento de teste disparado manualmente.

---

## Sprint 3 — Contas e Importação Inicial

**Objetivo:** ao conectar uma instituição, as contas do usuário são importadas automaticamente.

**Subtasks**
- [ ] Modelo ORM `Account` + migration (tabela `accounts`, Seção 5.2, incluindo `credit_data` jsonb)
- [ ] `domain/repositories/account_repository.py` + implementação
- [ ] `PluggyClient.get_accounts(item_id)` (`GET /accounts?itemId=`)
- [ ] Use case `ImportAccountsFromItem` — chamado a partir do `POST /pluggy/items` do Sprint 2, completando o fluxo de RF-012
- [ ] Endpoint `GET /accounts` (lista, RF-030)
- [ ] Endpoint `GET /accounts/{id}` (detalhe com extrato resumido, RF-031)
- [ ] Endpoint `POST /accounts` — criação de conta manual (RF-033, `type = MANUAL`)
- [ ] Endpoint `PATCH /accounts/{id}` — só permite editar contas manuais (RF-034)
- [ ] Endpoint `DELETE /accounts/{id}` — só contas manuais (RF-034)
- [ ] Regra de negócio: bloquear edição/exclusão de conta vinda de Pluggy com erro claro (`403`/`409`)
- [ ] Testes unitários e de integração de todos os endpoints acima, incluindo o caso de erro de edição de conta sincronizada

**DoD específico:** conectar um item de teste no Sandbox resulta nas contas aparecendo via `GET /accounts`; uma conta manual pode ser criada, editada e removida; uma conta Pluggy não pode.

---

## Sprint 4 — Transações e Sincronização

**Objetivo:** transações são importadas, mantidas atualizadas via webhook e nunca duplicadas.

**Subtasks**
- [ ] Modelo ORM `Transaction` + migration (tabela `transactions`, com `UNIQUE(account_id, pluggy_transaction_id)`, Seção 5.2/5.3)
- [ ] `domain/repositories/transaction_repository.py` + implementação
- [ ] `PluggyClient.get_transactions(account_id, cursor=...)` (`GET /v2/transactions`, paginação cursor-based, Seção 7.8)
- [ ] Use case `ImportTransactionsFromAccount` — importa histórico completo na conexão inicial (parte final de RF-012)
- [ ] Endpoint `GET /transactions` com filtros (`account_id`, `category_id`, `type`, `date_from`, `date_to`, `search`) e paginação (RF-040, RNF-002)
- [ ] Endpoint `GET /transactions/{id}` (detalhe)
- [ ] Endpoint `PATCH /transactions/{id}` — editar nota (RF-042); categoria será ligada no Sprint 5
- [ ] Endpoint `POST /transactions` — transação manual (RF-043)
- [ ] Endpoint `DELETE /transactions/{id}` — só manuais (RF-044)
- [ ] Endpoint `POST /transactions/{id}/split` — divisão em múltiplas categorias (RF-045, **stretch**: pode ser adiado para o Sprint 13 se o tempo apertar, mas o schema já deve suportar)
- [ ] Processamento completo do webhook (evoluindo o esqueleto do Sprint 2):
  - [ ] `item/created`, `item/updated`, `item/error` → atualizam `pluggy_items.status`
  - [ ] `transactions/created` → pagina `createdTransactionsLink` e insere novas transações
  - [ ] `transactions/updated` → rebusca `transactionIds` específicos e atualiza
  - [ ] `transactions/deleted` → remove/marca como removida
  - [ ] Idempotência garantida por `eventId` registrado + constraint única (Seção 7.5)
- [ ] Endpoint `POST /pluggy/items/{item_id}/sync` — sincronização manual forçada (RF-013)
- [ ] Job agendado no APScheduler: fallback de sync periódico para items com `last_synced_at` antigo (Seção 7.5, item 3)
- [ ] Tratamento de erro com retry exponencial (máx. 3 tentativas) nas chamadas à Pluggy (Seção 7.6)
- [ ] Registro de toda tentativa (sucesso/erro) em `sync_logs`
- [ ] Endpoint `GET /pluggy/items` (lista conexões com status, RF-013) e `DELETE /pluggy/items/{item_id}` (desconectar, RF-014, soft-delete)
- [ ] Testes: paginação por cursor, reenvio duplicado do mesmo webhook (garantir zero duplicação), simulação de erro de rede com retry, `LOGIN_ERROR` refletido corretamente

**DoD específico:** enviar o mesmo payload de webhook duas vezes não cria transações duplicadas (teste automatizado comprova); forçar sync manual atualiza `last_synced_at`; desconectar um item preserva as transações já importadas.

---

## Sprint 5 — Categorização Automática

**Objetivo:** toda transação nova recebe uma categoria automaticamente, com regras do usuário tendo prioridade.

**Subtasks**
- [ ] Modelo ORM `Category` + migration (tabela `categories`, com auto-relacionamento para subcategorias)
- [ ] Seed de categorias padrão do sistema (`is_system_default = true`) — ex.: Alimentação, Transporte, Moradia, Saúde, Lazer, Salário, etc.
- [ ] Modelo ORM `CategoryRule` + migration (tabela `category_rules`)
- [ ] `domain/services/categorization_engine.py` — regra pura (sem I/O), recebendo transação + regras ativas, retornando categoria sugerida + `category_source` (Seção 15, fluxo em cascata)
- [ ] Integrar o `CategorizationEngine` nos use cases de importação/atualização de transação dos Sprints 3–4 (toda transação nova passa pelo engine antes de salvar)
- [ ] Endpoints CRUD `GET/POST/PATCH/DELETE /categories` (RF-053)
- [ ] Endpoints CRUD `GET/POST/PATCH/DELETE /categories/rules` (RF-052)
- [ ] Endpoint `POST /categories/rules/preview` — simula quantas transações passadas seriam afetadas (RF-052)
- [ ] Endpoint `PATCH /transactions/{id}` estendido para aceitar `category_id` (sobrescrita manual → `category_source = MANUAL`, RF-041)
- [ ] Testes unitários exaustivos do `CategorizationEngine`: prioridade entre regras, regra `KEYWORD`/`MERCHANT_EXACT`/`REGEX`, ausência de match (fallback para categoria da Pluggy ou `UNCATEGORIZED`), sobrescrita manual não é revertida por nova regra

**DoD específico:** criar uma regra de categorização e rodar o preview mostra corretamente quantas transações existentes seriam categorizadas; uma nova transação simulada via teste é categorizada automaticamente sem intervenção manual.

---

## Sprint 6 — Orçamentos e Metas

**Objetivo:** usuário consegue planejar e acompanhar limites de gasto e metas financeiras.

**Subtasks**
- [ ] Modelo ORM `Budget` + migration (tabela `budgets`, constraint única por `user_id/category_id/reference_month`)
- [ ] `domain/services/budget_progress_calculator.py` — soma transações da categoria/mês e calcula % do limite (regra pura, testável)
- [ ] Endpoints CRUD `GET/POST/PATCH/DELETE /budgets` (RF-060)
- [ ] Endpoint `GET /budgets/{id}/progress` (RF-061)
- [ ] Endpoint `POST /budgets/duplicate-previous-month` (RF-063)
- [ ] Lógica de disparo de alerta ao ultrapassar 80%/100% — nesta sprint, apenas o **cálculo**; a criação efetiva do registro em `notifications` fica no Sprint 7 (tabela ainda não existe)
- [ ] Modelo ORM `Goal` + migration (tabela `goals`)
- [ ] Endpoints CRUD `GET/POST/PATCH/DELETE /goals` (RF-070)
- [ ] Endpoint `POST /goals/{id}/contribute` — aporte manual (RF-071)
- [ ] Lógica de meta vinculada a conta (`linked_account_id`): `current_amount` reflete o saldo da conta vinculada automaticamente (RF-071)
- [ ] Testes unitários do `BudgetProgressCalculator` (mês sem transações, categoria removida, limite zero/negativo tratado como erro de validação)
- [ ] Testes de integração dos endpoints de budgets e goals

**DoD específico:** criar um orçamento de R$500 para uma categoria e lançar transações de teste totalizando R$600 faz `GET /budgets/{id}/progress` retornar 120% corretamente; uma meta vinculada a conta reflete o saldo real da conta.

---

## Sprint 7 — Contas a Pagar e Notificações

**Objetivo:** usuário recebe lembretes de contas e alertas gerados pelo sistema em um único lugar.

**Subtasks**
- [ ] Modelo ORM `Bill` + migration (tabela `bills`)
- [ ] Modelo ORM `Notification` + migration (tabela `notifications`)
- [ ] Endpoints CRUD `GET/POST/PATCH/DELETE /bills` (RF-080)
- [ ] Endpoint `POST /bills/{id}/mark-paid` (RF-082)
- [ ] Job agendado (APScheduler): verifica `bills` cujo vencimento está a `reminder_days_before` dias e gera `notifications` do tipo `BILL_DUE` (RF-081)
- [ ] Lógica de matching automático (RF-083, **diferencial**): ao importar uma transação (Sprint 4), verificar se há `bill` compatível (valor aproximado + categoria + janela de datas) e sugerir vínculo via `linked_transaction_id`
- [ ] **Revisitar Sprint 4:** conectar o tratamento de erro de sync já existente para efetivamente criar `notifications` do tipo `SYNC_ERROR`
- [ ] **Revisitar Sprint 6:** conectar o cálculo de orçamento/meta para efetivamente criar `notifications` dos tipos `BUDGET_EXCEEDED` (uma única vez por categoria/mês, não a cada transação) e `GOAL_ACHIEVED`
- [ ] Endpoint `GET /notifications` (RF-100)
- [ ] Endpoint `PATCH /notifications/{id}/read` (RF-100)
- [ ] Testes: geração de lembrete de conta a pagar na janela correta, não duplicação de `BUDGET_EXCEEDED` no mesmo mês, matching de conta paga com transação real (incluindo falso positivo/negativo)

**DoD específico:** uma conta cadastrada com vencimento em 3 dias gera notificação `BILL_DUE` automaticamente pelo job agendado, verificável em `GET /notifications`.

---

## Sprint 8 — Relatórios, Exportação e Observabilidade

**Objetivo:** fechar o ciclo do backend com visão analítica dos dados e instrumentação de produção.

**Subtasks**
- [ ] Endpoint `GET /reports/summary?month=` (RF-090, base do dashboard)
- [ ] Endpoint `GET /reports/category-breakdown?month=` (RF-090)
- [ ] Endpoint `GET /reports/cashflow?from=&to=` (RF-091)
- [ ] Endpoint `GET /reports/net-worth-history` (RF-092)
- [ ] Endpoint `GET /reports/export?format=csv` (RF-093)
- [ ] Endpoint `GET /reports/export?format=pdf` (RF-093, **diferencial**, pode ser adiado)
- [ ] Integração com Sentry (`sentry-sdk`) — capturar exceptions não tratadas e erros de sincronização (Seção 11)
- [ ] Endpoint `GET /health` (liveness) e `GET /health/ready` (readiness: valida DB + validade do cache de `apiKey`, Seção 8.11)
- [ ] Auditoria: revisar todos os logs existentes das sprints anteriores para garantir que nenhum valor monetário/dado sensível é logado em texto claro (Seção 10.4)
- [ ] Rodar relatório de cobertura de testes (`pytest --cov`) e fechar lacunas até atingir a meta da RNF-008 (80% geral, 100% em regras financeiras críticas)
- [ ] Finalizar `backend-deploy.yml` (Seção 13.1) — deploy automático real (ainda em ambiente de teste/Sandbox) na PaaS escolhida
- [ ] Configurar backup automático do Postgres na PaaS (mesmo em ambiente de teste, para validar o processo)
- [ ] `README.md` do backend completo (como rodar, testar, configurar Pluggy Sandbox — Seção 20)

**DoD específico:** um erro proposital disparado em ambiente de teste aparece no Sentry; `pytest --cov` reporta a cobertura mínima definida; o backend está publicamente acessível (URL de teste) via deploy automático a partir do `main`.

---

## Sprint 9 — Fundação do App Flutter

**Objetivo:** esqueleto do app com infraestrutura de estado, rede e navegação prontos para receber features.

**Subtasks**
- [ ] `core/theme/`: design tokens (cores, tipografia, espaçamentos), `ThemeData` claro (e escuro, opcional)
- [ ] `core/router/`: configuração do `go_router` com rotas nomeadas e *guard* de autenticação (redireciona para login se não houver sessão válida)
- [ ] `core/network/`: `Dio` configurado com `baseUrl` via `--dart-define`, interceptor de header `Authorization`, interceptor de refresh automático (chama `/auth/refresh` transparente em `401`), interceptor de logging, header `X-Client-Platform` (Seção 10.2)
- [ ] `core/storage/`: wrapper de `flutter_secure_storage` para Android; estratégia de token em memória + cookie `HttpOnly` para Web (Seção 10.2) — implementar como interface única com duas implementações (`AndroidTokenStorage`/`WebTokenStorage`) selecionadas via `kIsWeb`
- [ ] `core/errors/`: `Failure` types e mapeamento do formato de erro do backend (RFC 7807-like) para exceções de domínio
- [ ] `core/utils/`: formatação de moeda (`NumberFormat.currency(locale: 'pt_BR')`) e data (`intl`)
- [ ] Configurar Riverpod (`ProviderScope` no `main.dart`) e `riverpod_generator`/`build_runner`
- [ ] Configurar `freezed`/`json_serializable` (build_runner) para os modelos de dados
- [ ] Completar `app-ci.yml`: `flutter analyze`, `flutter test --coverage`, `flutter build apk --debug`, `flutter build web`
- [ ] `README.md` do app completo (como rodar, gerar código, testar — Seção 20)

**DoD específico:** `flutter run -d chrome` e `flutter run -d <android>` sobem uma casca de app com tema aplicado e navegação entre 2 telas placeholder via `go_router`; pipeline de CI do app passa.

---

## Sprint 10 — Autenticação e Trava Local

**Objetivo:** usuário consegue logar, permanecer logado com renovação automática, e travar o app localmente no Android.

**Subtasks**
- [ ] Feature `auth/data`: datasource Dio (`login`, `refresh`, `logout`, `me`), DTOs (`freezed`)
- [ ] Feature `auth/domain`: entidade `User`, interface de repositório
- [ ] Feature `auth/presentation`: provider Riverpod de sessão (estado: `unauthenticated`/`authenticated`/`loading`), tela de login
- [ ] Persistência do `refresh_token` conforme estratégia por plataforma definida no Sprint 9
- [ ] Renovação automática de sessão ao abrir o app (checar token salvo antes de decidir rota inicial)
- [ ] Trava biométrica/PIN no Android via `local_auth`, exibida antes de liberar a navegação, mesmo com sessão JWT válida (RF-003)
- [ ] Tela/ação de logout (RF-004)
- [ ] Testes unitários do provider de sessão (mocktail no datasource)
- [ ] Testes widget da tela de login (estado de erro, loading, sucesso)

**DoD específico:** login funciona ponta a ponta contra o backend real; fechar e reabrir o app no Android exige biometria/PIN antes de mostrar qualquer dado.

---

## Sprint 11 — Onboarding e Conexão Pluggy

**Objetivo:** usuário consegue conectar o Banco Inter a partir do app, em Android e Web.

**Subtasks**
- [ ] Feature `onboarding_connect/data`: chamada a `POST /pluggy/connect-token`, chamada a `POST /pluggy/items`
- [ ] Tela "Adicionar conta" com CTA para iniciar o fluxo
- [ ] **Android:** integração com `flutter_inappwebview` carregando a URL hospedada do Pluggy Connect com o `connectToken`; captura dos callbacks `onSuccess`/`onError`/`onClose` via `addJavaScriptHandler` (Seção 7.4)
- [ ] **Web:** abertura do Pluggy Connect em nova aba (`url_launcher`/`dart:html`) com `oauthRedirectUri` apontando para rota `/connect/callback` do próprio app; tela de callback que consulta o backend para confirmar a criação do item (Seção 7.4, nota de implementação Web)
- [ ] Envio do `itemId` capturado para `POST /pluggy/items`
- [ ] Feature `onboarding_connect/presentation`: tela de gerenciamento de conexões — lista de `pluggy_items` com status (`Atualizado`, `Atualizando`, `Erro de login`, `Requer ação`), ação de forçar sync (`POST /pluggy/items/{id}/sync`) e ação de desconectar com confirmação (RF-013/RF-014)
- [ ] Texto explicativo na UI sobre a limitação de até 24h para atualização de transações em conectores Open Finance regulado (Seção 7.5, nota de atenção)
- [ ] Testes de integração do fluxo completo com backend mockado (simulando resposta de `connect-token` e criação de item)

**DoD específico:** rodando contra o Sandbox real da Pluggy, é possível concluir uma conexão de teste tanto no build Android quanto no build Web, e ver o item aparecer na tela de gerenciamento de conexões.

---

## Sprint 12 — Dashboard, Contas e Transações

**Objetivo:** as telas centrais de consulta financeira do dia a dia estão funcionais.

**Subtasks**
- [ ] Feature `dashboard`: tela inicial com saldo consolidado, saudação personalizada, gasto do mês vs. orçamento total, atalho para extrato recente (RF-020), indicador de contas a pagar próximas (RF-021), gráfico rápido de gasto por categoria (RF-022, `fl_chart`)
- [ ] Feature `accounts/presentation`: listagem de contas com saldo/fatura (RF-030), tela de detalhe com extrato paginado e filtro por período (RF-031), tela de detalhe de cartão de crédito (fatura, limite, vencimento — RF-032)
- [ ] Formulário de criação de conta manual (RF-033) e edição/exclusão (RF-034, com bloqueio de UI para contas Pluggy)
- [ ] Feature `transactions/presentation`: listagem com filtros (conta, categoria, tipo, período, busca textual — RF-040), scroll infinito/paginação
- [ ] Tela de detalhe de transação: edição de categoria (seletor) e nota (RF-041/RF-042)
- [ ] Formulário de criação de transação manual (RF-043) e exclusão (só manuais, RF-044)
- [ ] Tela/ação de split de transação (RF-045, **stretch** — pode ser adiada para o Sprint 13 se o endpoint do Sprint 4 também tiver sido adiado)
- [ ] Testes widget das listas (estado vazio, erro, carregando) e testes unitários dos providers de contas/transações

**DoD específico:** navegando pelo app é possível ver o dashboard com dados reais sincronizados, entrar em uma conta, ver o extrato, editar a categoria de uma transação e criar um lançamento manual — tudo refletindo no backend real.

---

## Sprint 13 — Categorias, Orçamentos, Metas e Contas a Pagar

**Objetivo:** o usuário consegue planejar (orçamentos/metas) e organizar (categorias/contas a pagar) diretamente pelo app.

**Subtasks**
- [ ] Feature `categories/presentation`: telas de gerenciamento de categorias/subcategorias (RF-053) e de regras de categorização, com preview do impacto antes de salvar (RF-052)
- [ ] Feature `budgets/presentation`: criação de orçamento por categoria (RF-060), barra/indicador de progresso com alerta visual em 80%/100% (RF-061), ação de duplicar orçamentos do mês anterior (RF-063)
- [ ] Feature `goals/presentation`: criação de meta (RF-070), tela de aporte manual e visualização de progresso, indicação de meta vinculada a conta (RF-071)
- [ ] Feature `bills/presentation`: cadastro de conta a pagar (recorrente ou pontual, RF-080), ação de marcar como paga (RF-082), indicação visual de sugestão de vínculo automático quando aplicável (RF-083)
- [ ] **Android:** agendamento de notificações locais (`flutter_local_notifications`) para vencimentos próximos, disparado após cada sincronização de `bills` (RF-101)
- [ ] Testes widget e unitários de cada tela/provider acima

**DoD específico:** é possível criar um orçamento, ultrapassar o limite com uma transação real e ver o alerta visual refletido; uma conta a pagar cadastrada gera notificação local no Android próximo ao vencimento.

---

## Sprint 14 — Relatórios, Notificações e Configurações

**Objetivo:** fechar as telas restantes de análise e administração do app.

**Subtasks**
- [ ] Feature `reports/presentation`: gráfico de pizza/barras de gasto por categoria (RF-090), gráfico de fluxo de caixa (RF-091), gráfico de linha de evolução patrimonial (RF-092) — todos com `fl_chart`
- [ ] Ação de exportação (RF-093): trigger de download do CSV gerado pelo backend (tratamento diferente para Web — download direto — e Android — salvar/compartilhar arquivo)
- [ ] Feature `notifications/presentation`: central de notificações (lista + contador de não lidas no ícone de sino), ação de marcar como lida (RF-100)
- [ ] Feature `settings/presentation`: tela de perfil (nome, e-mail, troca de senha — RF-110), acesso ao gerenciamento de categorias/regras (RF-111) e de conexões Pluggy (RF-112)
- [ ] Ação de exportação/backup completo dos dados do usuário (RF-113)
- [ ] Testes widget e unitários das telas acima

**DoD específico:** todos os relatórios da Seção 6.10 do PRD estão navegáveis com dados reais; a central de notificações reflete corretamente os alertas gerados pelo backend nas sprints anteriores.

---

## Sprint 15 — Testes End-to-End, Acessibilidade e Polimento

**Objetivo:** validar o sistema como um todo, não apenas por partes, e elevar a qualidade de UX antes de ir para produção real.

**Subtasks**
- [ ] Suíte de `integration_test` cobrindo os fluxos críticos completos: login → conectar conta → ver extrato sincronizado → criar orçamento → estourar orçamento → ver notificação
- [ ] Suíte equivalente no backend via `httpx.AsyncClient` cobrindo o mesmo fluxo ponta a ponta a nível de API (Seção 12.1)
- [ ] Revisão de acessibilidade: contraste AA (RNF-011), `Semantics` em botões/ícones interativos, tamanho de toque mínimo
- [ ] Golden tests das telas-chave (dashboard, extrato, orçamento) — **diferencial**, pode ser parcial
- [ ] Revisão geral de estados de erro/vazio/loading em todas as telas (nenhuma tela deve travar em branco silenciosamente)
- [ ] Revisão de performance: listagens grandes (extrato com centenas de transações) rolando sem travamentos perceptíveis
- [ ] Fechar lacunas finais de cobertura de testes em ambos os projetos

**DoD específico:** a suíte completa de `integration_test` e a suíte de API end-to-end do backend passam em CI; nenhuma tela do app apresenta estado quebrado nos cenários de erro testados manualmente (sem internet, backend fora do ar, Pluggy retornando erro).

---

## Sprint 16 — Produção: Segurança, Migração para Meu Pluggy e Deploy Final

**Objetivo:** sair do ambiente de testes (Sandbox) para uso real do dia a dia, com segurança de produção validada.

**Subtasks**
- [ ] Executar o checklist de segurança da Seção 10.5 do PRD item a item (segredos rotacionados, `DEBUG=False`, `/docs` protegido ou desabilitado, backup do Postgres confirmado, Sentry testado, webhook secret confirmado)
- [ ] Seguir o fluxo **Meu Pluggy** (Seção 7.2, passo 3): conectar a conta real do Banco Inter em `meu.pluggy.ai` e vincular à Aplicação criada no Dashboard
- [ ] Trocar `PLUGGY_CLIENT_ID`/`PLUGGY_CLIENT_SECRET` do ambiente de produção para o par correspondente ao uso real (fora do Sandbox)
- [ ] Repetir o fluxo de conexão (Sprint 11) agora contra dados reais, validando que contas e transações reais do Inter aparecem corretamente
- [ ] Deploy final do backend na PaaS escolhida (Railway/Render/Fly), com variáveis de ambiente de produção configuradas
- [ ] Deploy do build `flutter build web --release` na hospedagem estática escolhida
- [ ] Build e assinatura do `flutter build apk --release` (keystore próprio, armazenado como secret do GitHub) para instalação manual no celular
- [ ] Configurar domínio/URL final do app Web, ajustando `CORS_ALLOWED_ORIGINS` no backend de acordo (Seção 10.3)
- [ ] Período de observação ativa pós-deploy (alguns dias de uso real), acompanhando Sentry e logs, antes de considerar o sistema estável
- [ ] Revisão final da documentação (READMEs, `.env.example`, guia de configuração da Pluggy — Seção 20) para refletir o estado real de produção

**DoD específico:** o usuário consegue, no dia a dia, abrir o app (Android ou Web), ver o saldo real e as transações reais do Banco Inter sincronizadas automaticamente, sem nenhum dado de teste/Sandbox remanescente no ambiente de produção.

---

*Fim do backlog de sprints.*
