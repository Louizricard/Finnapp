# Finnapp — Frontend Flutter (Android & Web)

Aplicativo móvel e web do **Finnapp**, construído com Flutter e Dart 3, arquitetura Feature-First e Riverpod (ADR-005).

---

## Estrutura de Pastas (Feature-First)

```
app/
├── lib/
│   ├── core/                  # Utilitários globais, constantes, tema, roteamento, rede
│   │   ├── constants/
│   │   ├── theme/             # Design tokens e tema (Dark & Light)
│   │   ├── router/            # Rotas e guards
│   │   ├── network/           # Cliente HTTP
│   │   ├── storage/           # Armazenamento seguro de sessão
│   │   ├── errors/            # Tratamento de exceções
│   │   └── utils/             # Formatadores (moeda, data)
│   ├── features/              # Módulos organizados por funcionalidade
│   │   ├── auth/              # Autenticação e sessão
│   │   ├── onboarding_connect/# Conexão com Pluggy (WebView / redirect)
│   │   ├── dashboard/         # Resumo financeiro e visão geral
│   │   ├── accounts/          # Gestão de contas manuais e conectadas
│   │   ├── transactions/      # Extrato, busca e divisão de transações
│   │   ├── categories/        # Categorias e regras de categorização
│   │   ├── budgets/           # Orçamentos mensais
│   │   ├── goals/             # Metas financeiras
│   │   ├── bills/             # Contas a pagar e recorrências
│   │   ├── reports/           # Relatórios e fluxo de caixa
│   │   ├── notifications/     # Alertas e lembretes
│   │   └── settings/          # Configurações do usuário
│   ├── shared/                # Widgets e componentes reutilizáveis
│   │   └── widgets/
│   ├── app.dart               # Widget raiz da aplicação
│   └── main.dart              # Ponto de entrada
├── test/                      # Testes unitários e de widget
├── integration_test/          # Testes de integração E2E
├── pubspec.yaml               # Dependências do Flutter
└── analysis_options.yaml      # Regras estritas de linter
```

---

## Como Executar

### 1. Pré-requisitos
- Flutter 3.24+ (canal stable)
- Google Chrome (para desenvolvimento Web) ou Android Studio / emulador configurado

### 2. Rodando na Web (Chrome)

```bash
# Obter dependências
flutter pub get

# Se o Google Chrome estiver instalado via flatpak:
# export CHROME_EXECUTABLE=/var/lib/flatpak/exports/bin/com.google.Chrome

flutter run -d chrome
```

### 3. Rodando no Android

```bash
flutter run -d <android-device-or-emulator-id>
```

---

## Qualidade e Testes

```bash
# Análise estática com regras estritas
flutter analyze

# Execução de testes de unidade e widget
flutter test

# Compilação de teste para Web
flutter build web
```
