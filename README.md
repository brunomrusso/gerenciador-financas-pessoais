# 💰 CashFlow — Gerenciador de Finanças Pessoais

> Aplicação web completa de controle financeiro pessoal: receitas, descontos, despesas, cartões de crédito, transferências, investimentos, orçamentos e relatórios. Acessível pela web, instalável como PWA no celular e com bot Telegram integrado.

![Stack](https://img.shields.io/badge/stack-Flask%20%2B%20Svelte%20%2B%20PostgreSQL-blueviolet)
![PWA](https://img.shields.io/badge/PWA-installable-success)
![License](https://img.shields.io/badge/license-Personal-lightgrey)

---

## ✨ Funcionalidades

### 💼 Controle financeiro
- **Salário e receitas extras** com possibilidade de marcar como recorrente
- **Descontos** (INSS, plano de saúde, etc.) e créditos no salário
- **Despesas** categorizadas com tags, parcelas, recorrência, conta de pagamento
- **Cartões de crédito** com faturas mensais, parcelamento automático e múltiplas formas de pagamento da fatura
- **Transferências entre contas**
- **Investimentos** (aportes, saques, rendimentos) com saldo total acumulado
- **Múltiplas contas financeiras** (corrente, poupança, carteira, etc.)

### 📊 Visualização e análise
- **Cards de resumo** (receitas, descontos, despesas, investimentos, saldo final)
- **Gráfico de despesas por categoria** (pizza/donut)
- **Histórico** com gráfico de evolução mês a mês
- **Filtros** por descrição, categoria, conta, tag
- **Exportação para Excel** das despesas do mês

### 🎯 Orçamento
- **Orçamento por categoria** com alerta de estouro
- **Orçamento por tag** (#mercado, #lazer, etc.)
- **Indicadores visuais** de % consumido

### 🤖 Bot Telegram
- Lançamento rápido de despesas/receitas via menus inline
- Consulta de saldo e resumo do mês
- Vinculação segura via código de 6 dígitos

### 📱 Mobile-first / PWA
- Interface responsiva otimizada para celular (layout extrato)
- **Instalável como app** (Android/iOS) — ícone na tela inicial, fullscreen
- **Service Worker** para cache offline de assets
- Notação compacta de valores no mobile (sem cifrão)
- Auto-update quando nova versão é publicada

### 🔐 Segurança
- Autenticação por JWT
- Senha com hash (werkzeug)
- Reset de senha por email
- Modo "ocultar valores" (privacidade)

---

## 🏗️ Stack

| Camada | Tecnologias |
|---|---|
| **Backend** | Python 3.12, Flask 2.3, SQLAlchemy, Flask-JWT-Extended, Flask-CORS |
| **Banco** | PostgreSQL (produção) ou SQLite (dev) |
| **Frontend** | Svelte 4, TypeScript, Vite 5, Chart.js, Lucide Icons, SweetAlert2 |
| **PWA** | vite-plugin-pwa + Workbox |
| **Bot** | python-telegram-bot 21.x (polling em thread separada) |
| **Email** | SMTP (Gmail/personalizado) |
| **Deploy** | Render (backend) + Vercel (frontend) |
| **CI** | GitHub Actions (keepalive ping) |

---

## 📁 Estrutura

```
Financas/
├── app/                          # Backend Flask
│   ├── __init__.py               # App factory, blueprints, /health
│   ├── models.py                 # Modelos SQLAlchemy
│   ├── routes/                   # Endpoints REST (auth, records, cards, ...)
│   ├── telegram_bot/             # Bot Telegram (thread separada)
│   └── utils/                    # Mailer SMTP
├── frontend/                     # Frontend Svelte
│   ├── src/
│   │   ├── components/           # Componentes UI (SummaryCards, ExpenseTable, ...)
│   │   ├── pages/                # Login, Dashboard, ResetPassword
│   │   ├── stores/               # Stores Svelte (auth, ui, privacy, ...)
│   │   └── utils/                # Helpers (format BRL)
│   ├── public/assets/            # Ícones, logos
│   ├── vite.config.js            # Vite + PWA config
│   └── vercel.json               # Deploy Vercel
├── .github/workflows/
│   └── keepalive.yml             # Cron 13min para Render free não dormir
├── config.py                     # Configs por ambiente
├── run.py                        # Entrypoint gunicorn
├── init_db.py                    # Criar tabelas em DB novo
├── render.yaml                   # Config deploy Render
├── requirements.txt              # Dependências Python
├── setup.ps1 / start.ps1         # Scripts dev local (Windows)
└── SETUP.md / TROUBLESHOOTING.md / TUTORIAL_BOT.md
```

---

## 🚀 Setup local (Windows)

### Pré-requisitos
- Python 3.12
- Node.js 18+
- PostgreSQL 14+ (ou SQLite para teste rápido)

### Setup automático
```powershell
# Cria venv, instala dependências, prepara banco
.\setup.ps1

# Cria as tabelas
python init_db.py

# Inicia backend + frontend simultaneamente
.\start.ps1
```

### Setup manual
```powershell
# 1. Backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 2. Configurar .env (copie de .env.example)
copy .env.example .env
# edite DATABASE_URL e JWT_SECRET_KEY

# 3. Criar tabelas
python init_db.py

# 4. Rodar backend
python run.py
# disponível em http://localhost:5000

# 5. Frontend (em outro terminal)
cd frontend
npm install
npm run dev
# disponível em http://localhost:5173
```

Detalhes adicionais e troubleshooting: veja [`SETUP.md`](./SETUP.md) e [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md).

---

## 🔧 Variáveis de ambiente

Arquivo `.env` na raiz do projeto:

```bash
# Obrigatórias
DATABASE_URL=postgresql://user:password@localhost:5432/financas_db
JWT_SECRET_KEY=use-um-secret-aleatorio-longo-em-producao

# Ambiente Flask
FLASK_ENV=development        # development | production
FLASK_DEBUG=True             # False em produção

# Email (opcional, para reset de senha)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-app-password
SMTP_FROM=seu-email@gmail.com
APP_BASE_URL=http://localhost:5173

# Bot Telegram (opcional)
TELEGRAM_BOT_ENABLED=true
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_STARTUP_DELAY=10    # delay para evitar conflito de polling no redeploy
```

---

## 🚢 Deploy

### Backend — Render
1. Conecte o repositório ao Render (Web Service)
2. O `render.yaml` já configura tudo (build, start, healthcheck `/health`)
3. Configure as env vars (`DATABASE_URL`, `JWT_SECRET_KEY`, `SMTP_*`, `TELEGRAM_*`)
4. Deploy automático a cada push em `main`

### Frontend — Vercel
1. Conecte o repositório ao Vercel
2. **Root Directory**: `frontend`
3. **Build Command**: `npm run build`
4. **Output Directory**: `dist`
5. O `vercel.json` faz rewrite das chamadas `/api/*` para a URL do backend no Render

### Keep-alive (Render free)
O Render free coloca o serviço pra dormir após 15 min ociosos. O workflow `@/c:/Users/bruno/OneDrive/Documentos/Projetos/Financas/.github/workflows/keepalive.yml` pinga o endpoint `/health` a cada 13 min para manter ativo.

**Configuração**: cadastre a URL do backend como secret `RENDER_URL` em
`Settings → Secrets and variables → Actions`.

---

## 📱 PWA — Instalar no celular

### Android (Chrome/Edge)
1. Abra o site no celular
2. Toque em **Instalar** no toast que aparece (ou no menu do browser → "Adicionar à tela inicial")

### iOS (Safari)
1. Abra o site no Safari
2. Botão de compartilhar → **Adicionar à tela inicial**

Após instalado, o app abre fullscreen sem barra do browser, com ícone próprio na home.

---

## 🤖 Bot Telegram

1. Crie um bot no [@BotFather](https://t.me/BotFather) e copie o token
2. Configure `TELEGRAM_BOT_TOKEN` e `TELEGRAM_BOT_ENABLED=true` no `.env`
3. Reinicie o backend — o bot inicia em uma thread separada
4. No app web, vá em **Perfil → Telegram** e gere um código
5. No Telegram, envie `/start <código>` para o bot

Tutorial completo: [`TUTORIAL_BOT.md`](./TUTORIAL_BOT.md)

---

## 🛠️ Endpoints úteis

- `GET /health` — Healthcheck público (sem auth), usado pelo keepalive
- `POST /api/auth/register` — Registrar usuário
- `POST /api/auth/login` — Login (retorna JWT)
- `POST /api/auth/forgot-password` — Solicitar reset de senha
- `GET /api/records/:year/:month` — Registro mensal completo
- `GET /api/cards` — Cartões e faturas do mês
- `GET /api/accounts` — Contas financeiras com saldos calculados
- `GET /api/investments` — Investimentos

A maioria dos endpoints requer header `Authorization: Bearer <jwt>`.

---

## 📦 Scripts úteis

```powershell
# Dev
.\start.ps1               # backend + frontend
.\setup.ps1               # setup completo

# Backend
python run.py             # rodar backend
python init_db.py         # criar tabelas

# Frontend
cd frontend
npm run dev               # vite dev server
npm run build             # build produção
npm run preview           # servir build localmente
npm run check             # type-check svelte/ts
```

---

## 🔮 Roadmap / ideias

- [ ] Categorização automática por palavra-chave
- [ ] Detecção de duplicatas
- [ ] Metas mensais e gamificação
- [ ] Notificações Telegram (resumo diário, alertas de orçamento)
- [ ] Relatório anual estilo "Wrapped"
- [ ] OCR de cupom fiscal via bot
- [ ] Atalho `/d 45 almoço` no bot (parser rápido)
- [ ] Backup automático para Drive
- [ ] 2FA

---

## 📝 Licença

Projeto pessoal — uso restrito.

---

## 👤 Autor

**Bruno Russo** — desenvolvido como projeto pessoal de controle financeiro.