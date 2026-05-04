# 🚀 Guia Rápido de Setup

## Passo 1: Preparar o Backend

### 1.1 Criar ambiente virtual
```powershell
python -m venv venv
venv\Scripts\activate
```

### 1.2 Instalar dependências
```powershell
pip install -r requirements.txt
```

### 1.3 Configurar PostgreSQL

Você precisa ter PostgreSQL instalado. Se não tiver:
- Baixe em: https://www.postgresql.org/download/windows/
- Instale com a senha padrão `postgres`

Criar banco de dados:
```powershell
# Abra o pgAdmin ou use psql
psql -U postgres
CREATE DATABASE financas_db;
\q
```

### 1.4 Configurar .env
```powershell
# Copie o arquivo de exemplo
copy .env.example .env

# Edite .env com suas credenciais
# DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/financas_db
# JWT_SECRET_KEY=sua-chave-secreta-muito-segura
```

### 1.5 Iniciar o backend
```powershell
python run.py
```

O backend estará em: `http://localhost:5000`

## Passo 2: Preparar o Frontend

### 2.1 Instalar Node.js (se não tiver)
- Baixe em: https://nodejs.org/
- Instale a versão LTS

### 2.2 Instalar dependências do frontend
```powershell
cd frontend
npm install
```

### 2.3 Iniciar o frontend
```powershell
npm run dev
```

O frontend estará em: `http://localhost:5173`

## Passo 3: Testar a Aplicação

1. Abra `http://localhost:5173` no navegador
2. Clique em "Registrar" para criar uma conta
3. Use email: `teste@example.com` e senha: `teste123`
4. Após login, você verá o dashboard

## Passo 4: Migrar Dados (Opcional)

Se você tem dados no arquivo `controle_financeiro.xlsx`:

```powershell
# Certifique-se de que o backend está rodando
python migrate_data.py
```

Isso importará todos os dados do Excel para o PostgreSQL.

## ⚠️ Troubleshooting

### Erro: "psycopg2" não encontrado
```powershell
pip install psycopg2-binary
```

### Erro: Porta 5000 já em uso
```powershell
# Mude a porta em run.py
# Ou mate o processo usando a porta:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Erro: Porta 5173 já em uso
```powershell
cd frontend
npm run dev -- --port 5174
```

### Erro: "npm: comando não encontrado"
- Instale Node.js: https://nodejs.org/

### Erro de conexão com PostgreSQL
- Verifique se PostgreSQL está rodando
- Verifique as credenciais em `.env`
- Verifique o banco de dados foi criado: `CREATE DATABASE financas_db;`

## 📝 Próximos Passos

1. ✅ Backend rodando em `http://localhost:5000`
2. ✅ Frontend rodando em `http://localhost:5173`
3. ✅ Banco de dados PostgreSQL configurado
4. ⏳ Criar conta e fazer login
5. ⏳ Adicionar registros financeiros
6. ⏳ Visualizar histórico de 6 meses

## 🔗 Links Úteis

- Flask: https://flask.palletsprojects.com/
- Svelte: https://svelte.dev/
- PostgreSQL: https://www.postgresql.org/
- SQLAlchemy: https://www.sqlalchemy.org/

---

**Dúvidas?** Verifique o `README_NEW.md` para documentação completa.
