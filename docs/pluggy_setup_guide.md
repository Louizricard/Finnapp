# Guia de Configuração da Pluggy (Sandbox e Meu Pluggy)

Este documento orienta a configuração do ambiente Open Finance da **Pluggy** para o Finnapp, conforme especificado na Seção 7.2 do PRD.

---

## 1. Visão Geral

O Finnapp utiliza a Pluggy para sincronizar contas bancárias e transações financeiras.
- **Ambiente de Desenvolvimento:** **Sandbox** (dados fictícios simulados pela Pluggy para desenvolvimento e testes locais).
- **Ambiente de Produção (Uso Pessoal):** **Meu Pluggy** (`meu.pluggy.ai`), permitindo conexão gratuita com contas reais (ex: Banco Inter) vinculadas à aplicação.

> [!CAUTION]
> **Regra de Segurança Inegociável:** O `CLIENT_SECRET` e a `apiKey` da Pluggy NUNCA devem trafegar para o app Flutter ou ser expostos publicamente. Eles residem exclusivamente no backend (armazenados em variáveis de ambiente).

---

## 2. Passo a Passo no Sandbox (Desenvolvimento)

1. Acesse [pluggy.ai](https://pluggy.ai) e crie uma conta de desenvolvedor.
2. Acesse o **Dashboard da Pluggy**: [dashboard.pluggy.ai](https://dashboard.pluggy.ai).
3. Crie uma nova **Aplicação**:
   - Nome: `Finnapp Dev`
   - Modo: **Sandbox**
4. Obtenha as credenciais da aplicação:
   - `CLIENT_ID`: Copie para `PLUGGY_CLIENT_ID` no seu `.env` do backend.
   - `CLIENT_SECRET`: Copie para `PLUGGY_CLIENT_SECRET` no seu `.env` do backend.
5. Configure a URL base da Pluggy no `.env`:
   ```env
   PLUGGY_BASE_URL=https://api.pluggy.ai
   ```
6. Configure o segredo de webhook (utilizado a partir da Sprint 2/4):
   ```env
   PLUGGY_WEBHOOK_SECRET=seu-segredo-aleatorio
   ```

---

## 3. Passo a Passo para Uso Pessoal Real (Meu Pluggy)

Quando o backend e o frontend estiverem validados e prontos para uso pessoal real:
1. Acesse [meu.pluggy.ai](https://meu.pluggy.ai).
2. Conecte sua conta bancária real (ex: Banco Inter via Open Finance regulado).
3. No painel de integrações do Meu Pluggy, vincule a conexão à Aplicação criada no Dashboard da Pluggy.
4. Essa vinculação confere acesso contínuo e sem custo aos dados para fins de uso pessoal do desenvolvedor.
5. Repita o processo sempre que conectar uma nova instituição bancária.

---

## 4. Testes com Conectores Sandbox

No Sandbox, a Pluggy disponibiliza conectores mock com credenciais de teste:
- **Instituição Sandbox:** Banco Sandbox (ID específico da Pluggy)
- **Credenciais de teste:**
  - Usuário: `user-ok`
  - Senha: `password-ok`
  - (Para simular erro de login: `user-error` / `password-error`)
