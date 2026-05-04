# Sistema de Controle Financeiro - Versão 2.0

Aplicação modernizada de controle financeiro pessoal com backend em Flask + PostgreSQL e frontend em Svelte.

## 🚀 Arquitetura

- **Backend**: Flask + SQLAlchemy + PostgreSQL
- **Frontend**: Svelte + Vite
- **Autenticação**: JWT (JSON Web Tokens)
- **Banco de Dados**: PostgreSQL

## 📋 Pré-requisitos

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- pip e npm

## 🔧 Setup Backend

### 1. Criar ambiente virtual
```bash
cd c:\Users\bruno\OneDrive\Documentos\Projetos\Financas
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
```bash
# Copiar arquivo de exemplo
copy .env.example .env

# Editar .env com suas credenciais PostgreSQL
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/financas_db
# JWT_SECRET_KEY=sua-chave-secreta-aqui
```

### 4. Criar banco de dados PostgreSQL
```sql
CREATE DATABASE financas_db;
```

### 5. Inicializar banco de dados
```bash
python run.py
```

A aplicação criará automaticamente as tabelas na primeira execução.

### 6. Migrar dados do Excel (opcional)
Se você tem dados no arquivo `controle_financeiro.xlsx`:
```bash
python migrate_data.py
```

## 🎨 Setup Frontend

### 1. Instalar dependências
```bash
cd frontend
npm install
```

### 2. Iniciar servidor de desenvolvimento
```bash
npm run dev
```

O frontend estará disponível em `http://localhost:5173`

## 📚 Estrutura do Projeto

```
Financas/
├── app/
│   ├── __init__.py          # Inicialização da app Flask
│   ├── models.py            # Modelos SQLAlchemy
│   └── routes/
│       ├── auth_routes.py   # Rotas de autenticação
│       └── records_routes.py # Rotas de registros financeiros
├── frontend/
│   ├── src/
│   │   ├── pages/           # Páginas principais
│   │   ├── components/      # Componentes reutilizáveis
│   │   └── stores/          # Gerenciamento de estado
│   └── package.json
├── config.py                # Configuração da aplicação
├── run.py                   # Ponto de entrada do backend
├── migrate_data.py          # Script de migração de dados
└── requirements.txt         # Dependências Python
```

## 🔐 Autenticação

### Registrar novo usuário
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

### Fazer login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

Resposta:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "usuario@example.com"
  }
}
```

## 📊 API Endpoints

### Registros Financeiros
- `GET /api/records` - Listar registros
- `POST /api/records` - Criar novo registro
- `GET /api/records/{id}` - Obter detalhes
- `PUT /api/records/{id}` - Atualizar registro
- `DELETE /api/records/{id}` - Deletar registro

### Descontos e Créditos
- `POST /api/records/{id}/discounts` - Adicionar desconto
- `DELETE /api/records/discounts/{id}` - Deletar desconto

### Despesas
- `POST /api/records/{id}/expenses` - Adicionar despesa
- `DELETE /api/records/expenses/{id}` - Deletar despesa

### Investimentos
- `POST /api/records/{id}/investments` - Adicionar investimento
- `DELETE /api/records/investments/{id}` - Deletar investimento

### Histórico
- `GET /api/records/history?month=Janeiro&year=2024` - Histórico de 6 meses

### Categorias
- `GET /api/records/categories` - Listar categorias
- `POST /api/records/categories` - Criar categoria

## 🗄️ Schema do Banco de Dados

### users
```sql
id (PK) | email (UNIQUE) | password_hash | created_at | updated_at
```

### monthly_records
```sql
id (PK) | user_id (FK) | year | month | saldo_anterior | salario_bruto | created_at | updated_at
```

### discounts
```sql
id (PK) | record_id (FK) | descricao | valor | created_at
```

### expenses
```sql
id (PK) | record_id (FK) | descricao | valor | tipo | created_at
```

### card_details
```sql
id (PK) | record_id (FK) | card_name | valor | created_at
```

### investments
```sql
id (PK) | record_id (FK) | descricao | valor | created_at
```

### categories
```sql
id (PK) | user_id (FK) | nome | created_at
```

## 🚀 Deploy

### Backend (Heroku)
```bash
heroku create seu-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

### Frontend (Vercel/Netlify)
```bash
npm run build
# Deploy a pasta 'dist' para Vercel ou Netlify
```

## 🐛 Troubleshooting

### Erro de conexão com PostgreSQL
- Verifique se PostgreSQL está rodando
- Verifique as credenciais em `.env`
- Verifique se o banco de dados foi criado

### Erro de CORS
- Verifique se o backend está rodando em `http://localhost:5000`
- Verifique se o frontend está configurado para apontar para o backend correto

### Erro ao instalar dependências
```bash
# Limpar cache
pip cache purge
npm cache clean --force

# Reinstalar
pip install -r requirements.txt
npm install
```

## 📝 Notas de Migração

Os dados do Excel foram migrados para o PostgreSQL com a seguinte estrutura:
- Cada linha do Excel virou um registro mensal
- Descontos e créditos foram separados em uma tabela própria
- Despesas foram separadas em uma tabela própria
- Investimentos foram separados em uma tabela própria
- Detalhes de cartão foram separados em uma tabela própria

## 📄 Licença

MIT

## 👤 Autor

Seu Nome

---

**Última atualização**: Maio 2024
