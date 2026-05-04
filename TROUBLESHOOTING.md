# Troubleshooting - Guia de Solução de Problemas

## Problemas Comuns e Soluções

### 1. Erro: "psql não é reconhecido"

**Problema:**
```
psql : O termo 'psql' não é reconhecido como nome de cmdlet
```

**Causa:** PostgreSQL não está instalado ou não está no PATH do Windows

**Solução:**
1. Instale PostgreSQL: https://www.postgresql.org/download/windows/
2. Durante a instalação, marque "Add PostgreSQL to PATH"
3. Reinicie o PowerShell
4. Execute novamente: `powershell -ExecutionPolicy Bypass -File install.ps1`

**Alternativa:** Use o script rápido que não verifica PostgreSQL:
```powershell
powershell -ExecutionPolicy Bypass -File quick_setup.ps1
```

---

### 2. Erro: "ModuleNotFoundError: No module named 'pkg_resources'"

**Problema:**
```
ModuleNotFoundError: No module named 'pkg_resources'
[ERRO] Erro ao instalar dependencias Python
```

**Causa:** Versão desatualizada de pip/setuptools

**Solução:**
O script agora trata isso automaticamente. Se ainda tiver problema:

```powershell
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Atualizar pip e setuptools
python -m pip install --upgrade pip setuptools wheel

# Instalar dependências com fallback
pip install -r requirements.txt --no-build-isolation
```

---

### 3. Erro: "Porta 5000 já em uso"

**Problema:**
```
Address already in use
```

**Causa:** Outro processo está usando a porta 5000

**Solução:**

Opção 1: Matar o processo que está usando a porta
```powershell
# Encontrar processo na porta 5000
netstat -ano | findstr :5000

# Matar o processo (substitua PID pelo número encontrado)
taskkill /PID <PID> /F
```

Opção 2: Mudar a porta no arquivo `run.py`
```python
# Mude de:
app.run(debug=True, host='127.0.0.1', port=5000)

# Para:
app.run(debug=True, host='127.0.0.1', port=5001)
```

---

### 4. Erro: "Porta 5173 já em uso"

**Problema:**
```
Port 5173 is in use
```

**Causa:** Outro processo está usando a porta 5173

**Solução:**

Opção 1: Matar o processo
```powershell
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

Opção 2: Mudar a porta em `frontend/vite.config.js`
```javascript
server: {
  port: 5174  // Mude para outra porta
}
```

---

### 5. Erro: "npm: comando não encontrado"

**Problema:**
```
npm : O termo 'npm' não é reconhecido
```

**Causa:** Node.js não está instalado

**Solução:**
1. Instale Node.js: https://nodejs.org/
2. Escolha a versão LTS
3. Reinicie o PowerShell
4. Verifique: `node --version` e `npm --version`

---

### 6. Erro: "python: comando não encontrado"

**Problema:**
```
python : O termo 'python' não é reconhecido
```

**Causa:** Python não está instalado ou não está no PATH

**Solução:**
1. Instale Python: https://www.python.org/
2. **IMPORTANTE:** Marque "Add Python to PATH" durante a instalação
3. Reinicie o PowerShell
4. Verifique: `python --version`

---

### 7. Erro: "Arquivo .env não encontrado"

**Problema:**
```
[ERRO] Arquivo .env não encontrado!
```

**Causa:** Arquivo .env não foi criado

**Solução:**
```powershell
# Copiar arquivo de exemplo
Copy-Item ".env.example" ".env"

# Editar arquivo
notepad .env
```

Preencha com suas credenciais PostgreSQL:
```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/financas_db
JWT_SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=development
FLASK_DEBUG=True
```

---

### 8. Erro: "Banco de dados não existe"

**Problema:**
```
FATAL: database "financas_db" does not exist
```

**Causa:** Banco de dados não foi criado

**Solução:**
```powershell
# Executar script de criação de banco
powershell -ExecutionPolicy Bypass -File create_db.ps1

# Ou criar manualmente
psql -U postgres
CREATE DATABASE financas_db;
\q
```

---

### 9. Erro: "Acesso negado ao executar script"

**Problema:**
```
Não é possível carregar o arquivo install.ps1 porque a execução de scripts foi desabilitada
```

**Causa:** Política de execução do PowerShell está restritiva

**Solução:**
```powershell
# Executar com -ExecutionPolicy Bypass
powershell -ExecutionPolicy Bypass -File install.ps1

# Ou alterar política globalmente (requer admin)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### 10. Erro: "Ambiente virtual não ativa"

**Problema:**
```
& : O arquivo não pode ser carregado porque a execução de scripts foi desabilitada
```

**Causa:** Política de execução do PowerShell

**Solução:**
```powershell
# Ativar manualmente
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Ou usar cmd.exe em vez de PowerShell
cmd.exe
venv\Scripts\activate.bat
```

---

## Fluxo de Troubleshooting

Se tiver problema, siga este fluxo:

1. **Verifique pré-requisitos:**
   ```powershell
   python --version
   node --version
   npm --version
   ```

2. **Se algum não funcionar, instale:**
   - Python: https://www.python.org/
   - Node.js: https://nodejs.org/
   - PostgreSQL: https://www.postgresql.org/

3. **Tente o setup rápido:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File quick_setup.ps1
   ```

4. **Se ainda tiver erro, tente manualmente:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt --no-build-isolation
   cd frontend
   npm install
   cd ..
   ```

5. **Se nada funcionar, abra uma issue no repositório**

---

## Comandos Úteis

### Verificar portas em uso
```powershell
netstat -ano | findstr :5000  # Porta 5000
netstat -ano | findstr :5173  # Porta 5173
```

### Matar processo por porta
```powershell
taskkill /PID <PID> /F
```

### Limpar cache do pip
```powershell
pip cache purge
```

### Limpar node_modules
```powershell
cd frontend
Remove-Item node_modules -Recurse -Force
npm install
```

### Reinstalar tudo do zero
```powershell
# Remover ambiente virtual
Remove-Item venv -Recurse -Force

# Remover node_modules
cd frontend
Remove-Item node_modules -Recurse -Force
cd ..

# Executar setup novamente
powershell -ExecutionPolicy Bypass -File quick_setup.ps1
```

---

## Contato e Suporte

Se o problema persistir:

1. Verifique a documentação: `README_NEW.md`
2. Consulte o guia de testes: `TESTE_RAPIDO.md`
3. Abra uma issue no repositório: https://github.com/brunomrusso/gerenciador-financas-pessoais

---

**Última atualização:** Maio 4, 2024

**Versão:** 1.0
