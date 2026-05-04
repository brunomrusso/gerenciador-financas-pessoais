# Script de Setup Automatico - Sistema de Controle Financeiro
# Execute como: powershell -ExecutionPolicy Bypass -File setup.ps1

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Setup Automatico - Sistema de Controle Financeiro" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

# Cores para output
$success = "Green"
$errorColor = "Red"
$info = "Cyan"
$warning = "Yellow"

# 1. Verificar Python
Write-Host "[1/8] Verificando Python..." -ForegroundColor $info
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Python encontrado: $pythonCheck" -ForegroundColor $success
} else {
    Write-Host "   [ERRO] Python nao encontrado. Instale em: https://www.python.org/" -ForegroundColor $errorColor
    exit 1
}

# 2. Verificar Node.js
Write-Host ""
Write-Host "[2/8] Verificando Node.js..." -ForegroundColor $info
$nodeCheck = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Node.js encontrado: $nodeCheck" -ForegroundColor $success
} else {
    Write-Host "   [ERRO] Node.js nao encontrado. Instale em: https://nodejs.org/" -ForegroundColor $errorColor
    exit 1
}

# 3. Verificar PostgreSQL
Write-Host ""
Write-Host "[3/8] Verificando PostgreSQL..." -ForegroundColor $info
$psqlCheck = psql --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] PostgreSQL encontrado: $psqlCheck" -ForegroundColor $success
} else {
    Write-Host "   [AVISO] PostgreSQL nao encontrado. Instale em: https://www.postgresql.org/" -ForegroundColor $warning
    Write-Host "   Continuando mesmo assim..." -ForegroundColor $warning
}

# 4. Criar ambiente virtual Python
Write-Host ""
Write-Host "[4/8] Criando ambiente virtual Python..." -ForegroundColor $info
if (Test-Path "venv") {
    Write-Host "   [AVISO] Ambiente virtual ja existe" -ForegroundColor $warning
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Ambiente virtual criado" -ForegroundColor $success
    } else {
        Write-Host "   [ERRO] Erro ao criar ambiente virtual" -ForegroundColor $errorColor
        exit 1
    }
}

# 5. Ativar ambiente virtual
Write-Host ""
Write-Host "[5/8] Ativando ambiente virtual..." -ForegroundColor $info
& ".\venv\Scripts\Activate.ps1"
Write-Host "   [OK] Ambiente virtual ativado" -ForegroundColor $success

# 6. Instalar dependencias Python
Write-Host ""
Write-Host "[6/8] Instalando dependencias Python..." -ForegroundColor $info
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Dependencias Python instaladas" -ForegroundColor $success
} else {
    Write-Host "   [ERRO] Erro ao instalar dependencias Python" -ForegroundColor $errorColor
    exit 1
}

# 7. Criar arquivo .env
Write-Host ""
Write-Host "[7/8] Configurando variaveis de ambiente..." -ForegroundColor $info
if (Test-Path ".env") {
    Write-Host "   [AVISO] Arquivo .env ja existe" -ForegroundColor $warning
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "   [OK] Arquivo .env criado" -ForegroundColor $success
    Write-Host "   [AVISO] IMPORTANTE: Edite .env com suas credenciais PostgreSQL" -ForegroundColor $warning
}

# 8. Instalar dependencias Frontend
Write-Host ""
Write-Host "[8/8] Instalando dependencias Frontend..." -ForegroundColor $info
Push-Location "frontend"
npm install --silent
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Dependencias Frontend instaladas" -ForegroundColor $success
} else {
    Write-Host "   [ERRO] Erro ao instalar dependencias Frontend" -ForegroundColor $errorColor
    Pop-Location
    exit 1
}
Pop-Location

# Resumo
Write-Host ""
Write-Host "===================================================================" -ForegroundColor $success
Write-Host "  [SUCESSO] SETUP CONCLUIDO!" -ForegroundColor $success
Write-Host "===================================================================" -ForegroundColor $success

Write-Host ""
Write-Host "[PROXIMOS PASSOS]" -ForegroundColor $info
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
Write-Host "5. Acesse a aplicacao:" -ForegroundColor $info
Write-Host "   http://localhost:5173" -ForegroundColor $warning
Write-Host ""
