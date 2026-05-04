# 🧪 Guia de Teste Rápido

## Teste 1: Backend (API)

### 1.1 Iniciar o backend
```powershell
cd c:\Users\bruno\OneDrive\Documentos\Projetos\Financas
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edite .env com suas credenciais PostgreSQL
python run.py
```

Você deve ver:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 1.2 Testar endpoints com curl ou Postman

**Registrar usuário:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@example.com","password":"teste123"}'
```

Resposta esperada:
```json
{
  "message": "Usuário criado com sucesso",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "teste@example.com",
    "created_at": "2024-05-04T..."
  }
}
```

**Fazer login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@example.com","password":"teste123"}'
```

**Criar registro mensal:**
```bash
curl -X POST http://localhost:5000/api/records \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "month":"Janeiro",
    "year":2024,
    "saldo_anterior":1000,
    "salario_bruto":5000
  }'
```

**Listar registros:**
```bash
curl -X GET "http://localhost:5000/api/records?month=Janeiro&year=2024" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## Teste 2: Frontend (Svelte)

### 2.1 Instalar e iniciar
```powershell
cd c:\Users\bruno\OneDrive\Documentos\Projetos\Financas\frontend
npm install
npm run dev
```

Você deve ver:
```
VITE v5.0.0  ready in XXX ms

➜  Local:   http://localhost:5173/
```

### 2.2 Testar no navegador

1. Abra `http://localhost:5173` no navegador
2. Você deve ver a tela de login
3. Clique em "Registrar"
4. Preencha:
   - Email: `teste@example.com`
   - Senha: `teste123`
5. Clique em "Registrar"
6. Você deve ser redirecionado para o dashboard

### 2.3 Testar funcionalidades

**Dashboard:**
- ✅ Deve mostrar seletor de mês/ano
- ✅ Deve mostrar cards de resumo (Receitas, Descontos, Despesas, Investimentos, Saldo)
- ✅ Deve mostrar abas "Detalhes" e "Histórico"

**Detalhes:**
- ✅ Deve permitir editar Saldo Anterior
- ✅ Deve permitir editar Salário Bruto
- ✅ Deve mostrar tabelas vazias (sem dados ainda)

**Histórico:**
- ✅ Deve mostrar gráfico com dados dos últimos 6 meses

---

## Teste 3: Migração de dados

### 3.1 Preparar dados
Certifique-se de que você tem um arquivo `controle_financeiro.xlsx` com dados.

### 3.2 Executar migração
```powershell
# Certifique-se de que o backend está rodando
python migrate_data.py
```

Você deve ver:
```
Migrando dados para usuário: admin@financas.local
✓ Migrado: Janeiro/2024
✓ Migrado: Fevereiro/2024
...
=== Migração Concluída ===
Registros migrados: X
Registros pulados: Y
```

### 3.3 Verificar dados no frontend
1. Faça login com `admin@financas.local` / `admin123`
2. Selecione um mês que foi migrado
3. Você deve ver os dados no dashboard

---

## Teste 4: Banco de Dados

### 4.1 Conectar ao PostgreSQL
```powershell
psql -U postgres -d financas_db
```

### 4.2 Verificar tabelas
```sql
\dt
```

Você deve ver:
```
           List of relations
 Schema |       Name        | Type  | Owner
--------+-------------------+-------+----------
 public | card_details      | table | postgres
 public | categories        | table | postgres
 public | discounts         | table | postgres
 public | expenses          | table | postgres
 public | investments       | table | postgres
 public | monthly_records   | table | postgres
 public | users             | table | postgres
```

### 4.3 Verificar dados
```sql
SELECT * FROM users;
SELECT * FROM monthly_records;
SELECT * FROM discounts;
```

---

## ✅ Checklist de Teste

- [ ] Backend inicia sem erros
- [ ] Frontend inicia sem erros
- [ ] Consegue registrar novo usuário
- [ ] Consegue fazer login
- [ ] Dashboard carrega após login
- [ ] Seletor de mês/ano funciona
- [ ] Cards de resumo mostram valores
- [ ] Tabelas de dados carregam
- [ ] Gráfico de histórico renderiza
- [ ] Dados do Excel foram migrados (se aplicável)
- [ ] Banco de dados tem todas as tabelas

---

## 🐛 Troubleshooting

### Backend não inicia
```
Error: could not translate host name "localhost" to address
```
**Solução**: Verifique se PostgreSQL está rodando e as credenciais em `.env` estão corretas.

### Frontend não conecta ao backend
```
Failed to fetch
```
**Solução**: Verifique se o backend está rodando em `http://localhost:5000`

### Erro ao instalar dependências
```
pip: command not found
```
**Solução**: Ative o ambiente virtual: `venv\Scripts\activate`

### Porta já em uso
```
Address already in use
```
**Solução**: Mude a porta em `run.py` ou `frontend/vite.config.js`

---

## 📊 Dados de teste

Use esses dados para testar manualmente:

**Saldo Anterior**: 1000
**Salário Bruto**: 5000

**Descontos:**
- INSS: -500
- IR: -300
- Bônus: +500

**Despesas:**
- Aluguel: -1500
- Alimentação: -400
- Transporte: -200

**Investimentos:**
- Poupança: -1000
- Ações: -500

---

## 🎯 Resultado esperado

Após todos os testes, você deve ter:
- ✅ Backend rodando em `http://localhost:5000`
- ✅ Frontend rodando em `http://localhost:5173`
- ✅ Banco de dados PostgreSQL com dados
- ✅ Autenticação funcionando
- ✅ Dashboard mostrando dados corretamente

**Tempo estimado**: 30 minutos

---

**Dúvidas?** Consulte `README_NEW.md` ou `SETUP.md`
