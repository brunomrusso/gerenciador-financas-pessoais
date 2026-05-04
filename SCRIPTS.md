# 🤖 Guia de Scripts de Automação

Este projeto inclui scripts PowerShell para automatizar a instalação e execução da aplicação.

---

## 📋 Scripts Disponíveis

### 1. **install.ps1** - Instalação Completa (Recomendado)
Menu interativo que permite escolher qual etapa executar.

**Uso:**
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

**Opções:**
- 1️⃣ Instalação Completa (Setup + BD + Migração + Iniciar)
- 2️⃣ Apenas Setup
- 3️⃣ Criar Banco de Dados
- 4️⃣ Migrar Dados
- 5️⃣ Iniciar Aplicação

---

### 2. **setup.ps1** - Setup Inicial
Instala todas as dependências (Python e Node.js).

**Uso:**
```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

**O que faz:**
- ✅ Verifica Python
- ✅ Verifica Node.js
- ✅ Verifica PostgreSQL
- ✅ Cria ambiente virtual Python
- ✅ Instala dependências Python
- ✅ Cria arquivo .env
- ✅ Instala dependências Node.js

**Tempo:** ~5 minutos

---

### 3. **create_db.ps1** - Criar Banco de Dados
Cria o banco de dados PostgreSQL automaticamente.

**Uso:**
```powershell
powershell -ExecutionPolicy Bypass -File create_db.ps1
```

**O que faz:**
- ✅ Verifica PostgreSQL
- ✅ Solicita credenciais
- ✅ Cria banco de dados `financas_db`
- ✅ Atualiza arquivo .env

**Tempo:** ~1 minuto

---

### 4. **migrate.ps1** - Migrar Dados
Importa dados do Excel para PostgreSQL.

**Uso:**
```powershell
powershell -ExecutionPolicy Bypass -File migrate.ps1
```

**Pré-requisitos:**
- Arquivo `controle_financeiro.xlsx` na pasta raiz
- Arquivo `.env` configurado
- Backend rodando (opcional)

**O que faz:**
- ✅ Verifica arquivo Excel
- ✅ Ativa ambiente virtual
- ✅ Executa script de migração
- ✅ Mostra relatório

**Tempo:** ~2 minutos

---

### 5. **start.ps1** - Iniciar Aplicação
Inicia Backend e Frontend simultaneamente.

**Uso:**
```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

**O que faz:**
- ✅ Ativa ambiente virtual
- ✅ Inicia Backend (Flask) em background
- ✅ Inicia Frontend (Svelte) em background
- ✅ Monitora processos
- ✅ Permite parar com Ctrl+C

**Acessar:**
- Frontend: http://localhost:5173
- Backend: http://localhost:5000

**Tempo:** ~5 segundos

---

## 🚀 Fluxo Recomendado

### Primeira Vez (Instalação Completa)

```powershell
# Opção 1: Usar o script master (recomendado)
powershell -ExecutionPolicy Bypass -File install.ps1
# Escolha opção 1

# Opção 2: Executar manualmente
powershell -ExecutionPolicy Bypass -File setup.ps1
powershell -ExecutionPolicy Bypass -File create_db.ps1
powershell -ExecutionPolicy Bypass -File migrate.ps1  # Se tiver dados
powershell -ExecutionPolicy Bypass -File start.ps1
```

### Próximas Vezes (Apenas Iniciar)

```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

---

## 🔧 Solução de Problemas

### Erro: "PowerShell não reconhece o comando"

**Solução:** Use o caminho completo
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\bruno\OneDrive\Documentos\Projetos\Financas\install.ps1"
```

### Erro: "Acesso negado"

**Solução:** Execute como Administrador
```powershell
# Clique com botão direito em PowerShell e escolha "Executar como Administrador"
powershell -ExecutionPolicy Bypass -File install.ps1
```

### Erro: "Python não encontrado"

**Solução:** Instale Python
- https://www.python.org/
- Marque "Add Python to PATH" durante instalação

### Erro: "Node.js não encontrado"

**Solução:** Instale Node.js
- https://nodejs.org/
- Instale a versão LTS

### Erro: "PostgreSQL não encontrado"

**Solução:** Instale PostgreSQL
- https://www.postgresql.org/
- Lembre-se da senha do usuário `postgres`

### Erro: "Porta 5000 já em uso"

**Solução:** Mude a porta em `run.py`
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Use 5001 em vez de 5000
```

### Erro: "Porta 5173 já em use"

**Solução:** Mude a porta em `frontend/vite.config.js`
```javascript
server: {
  port: 5174  // Use 5174 em vez de 5173
}
```

---

## 📊 Variáveis de Ambiente

Os scripts criam automaticamente um arquivo `.env` com:

```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/financas_db
JWT_SECRET_KEY=sua-chave-secreta-muito-segura
FLASK_ENV=development
FLASK_DEBUG=True
```

**Edite conforme necessário:**
```powershell
notepad .env
```

---

## 🔐 Segurança

### Senhas
- A senha do PostgreSQL é solicitada durante `create_db.ps1`
- Não é armazenada em arquivos de log
- Use uma senha forte em produção

### JWT_SECRET_KEY
- Gerada aleatoriamente durante `create_db.ps1`
- Mude em produção para uma chave mais segura
- Nunca compartilhe a chave

---

## 📈 Monitoramento

### Ver processos rodando

```powershell
# Ver todos os processos Python
Get-Process python

# Ver todos os processos Node
Get-Process node
```

### Parar processos

```powershell
# Parar Python
Stop-Process -Name python

# Parar Node
Stop-Process -Name node
```

---

## 🎯 Dicas

1. **Crie um atalho** para executar `start.ps1` rapidamente
2. **Use um terminal separado** para cada script
3. **Monitore os logs** para erros
4. **Faça backup** do arquivo `.env`
5. **Atualize dependências** regularmente com `pip install -r requirements.txt --upgrade`

---

## 📞 Suporte

Se tiver problemas:
1. Verifique se todas as dependências estão instaladas
2. Consulte `SETUP.md` para troubleshooting
3. Verifique os logs de erro
4. Abra uma issue no repositório

---

## 🔄 Atualizar Dependências

```powershell
# Python
pip install -r requirements.txt --upgrade

# Node.js
cd frontend
npm update
```

---

**Última atualização**: Maio 4, 2024

**Versão**: 1.0

---

*Scripts criados para facilitar a vida! 🎉*
