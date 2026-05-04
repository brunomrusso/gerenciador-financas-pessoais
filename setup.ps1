# Script de Setup Automático - Sistema de Controle Financeiro
# Execute como: powershell -ExecutionPolicy Bypass -File setup.ps1

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     🚀 Setup Automático - Sistema de Controle Financeiro      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Cores para output
$success = "Green"
$error = "Red"
$info = "Cyan"
$warning = "Yellow"

# 1. Verificar Python
Write-Host "1️⃣  Verificando Python..." -ForegroundColor $info
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Python encontrado: $pythonCheck" -ForegroundColor $success
} else {
    Write-Host "   ❌ Python não encontrado. Instale em: https://www.python.org/" -ForegroundColor $error
    exit 1
}

# 2. Verificar Node.js
Write-Host ""
Write-Host "2️⃣  Verificando Node.js..." -ForegroundColor $info
$nodeCheck = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Node.js encontrado: $nodeCheck" -ForegroundColor $success
} else {
    Write-Host "   ❌ Node.js não encontrado. Instale em: https://nodejs.org/" -ForegroundColor $error
    exit 1
}

# 3. Verificar PostgreSQL
Write-Host ""
Write-Host "3️⃣  Verificando PostgreSQL..." -ForegroundColor $info
$psqlCheck = psql --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ PostgreSQL encontrado: $psqlCheck" -ForegroundColor $success
} else {
    Write-Host "   ⚠️  PostgreSQL não encontrado. Instale em: https://www.postgresql.org/" -ForegroundColor $warning
    Write-Host "   Continuando mesmo assim..." -ForegroundColor $warning
}

# 4. Criar ambiente virtual Python
Write-Host ""
Write-Host "4️⃣  Criando ambiente virtual Python..." -ForegroundColor $info
if (Test-Path "venv") {
    Write-Host "   ⚠️  Ambiente virtual já existe" -ForegroundColor $warning
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Ambiente virtual criado" -ForegroundColor $success
    } else {
        Write-Host "   ❌ Erro ao criar ambiente virtual" -ForegroundColor $error
        exit 1
    }
}

# 5. Ativar ambiente virtual
Write-Host ""
Write-Host "5️⃣  Ativando ambiente virtual..." -ForegroundColor $info
& ".\venv\Scripts\Activate.ps1"
Write-Host "   ✅ Ambiente virtual ativado" -ForegroundColor $success

# 6. Instalar dependências Python
Write-Host ""
Write-Host "6️⃣  Instalando dependências Python..." -ForegroundColor $info
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Dependências Python instaladas" -ForegroundColor $success
} else {
    Write-Host "   ❌ Erro ao instalar dependências Python" -ForegroundColor $error
    exit 1
}

# 7. Criar arquivo .env
Write-Host ""
Write-Host "7️⃣  Configurando variáveis de ambiente..." -ForegroundColor $info
if (Test-Path ".env") {
    Write-Host "   ⚠️  Arquivo .env já existe" -ForegroundColor $warning
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "   ✅ Arquivo .env criado" -ForegroundColor $success
    Write-Host "   ⚠️  IMPORTANTE: Edite .env com suas credenciais PostgreSQL" -ForegroundColor $warning
}

# 8. Instalar dependências Frontend
Write-Host ""
Write-Host "8️⃣  Instalando dependências Frontend..." -ForegroundColor $info
Push-Location "frontend"
npm install --silent
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Dependências Frontend instaladas" -ForegroundColor $success
} else {
    Write-Host "   ❌ Erro ao instalar dependências Frontend" -ForegroundColor $error
    Pop-Location
    exit 1
}
Pop-Location

# 9. Criar banco de dados PostgreSQL
Write-Host ""
Write-Host "9️⃣  Criando banco de dados PostgreSQL..." -ForegroundColor $info
Write-Host "   ℹ️  Execute no PostgreSQL (psql):" -ForegroundColor $info
Write-Host "   CREATE DATABASE financas_db;" -ForegroundColor $warning

# 10. Resumo
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor $success
Write-Host "║                    ✅ SETUP CONCLUÍDO!                         ║" -ForegroundColor $success
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor $success

Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor $info
Write-Host ""
Write-Host "1. Edite o arquivo .env com suas credenciais PostgreSQL:" -ForegroundColor $info
Write-Host "   DATABASE_URL=postgresql://usuario:senha@localhost:5432/financas_db" -ForegroundColor $warning
Write-Host ""
Write-Host "2. Crie o banco de dados no PostgreSQL:" -ForegroundColor $info
Write-Host "   psql -U postgres" -ForegroundColor $warning
Write-Host "   CREATE DATABASE financas_db;" -ForegroundColor $warning
Write-Host ""
Write-Host "3. Inicie o backend:" -ForegroundColor $info
Write-Host "   python run.py" -ForegroundColor $warning
Write-Host ""
Write-Host "4. Em outro terminal, inicie o frontend:" -ForegroundColor $info
Write-Host "   cd frontend" -ForegroundColor $warning
Write-Host "   npm run dev" -ForegroundColor $warning
Write-Host ""
Write-Host "5. Acesse a aplicação:" -ForegroundColor $info
Write-Host "   http://localhost:5173" -ForegroundColor $warning
Write-Host ""
