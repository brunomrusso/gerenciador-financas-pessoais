# Script de Setup Rapido - Apenas instala dependencias (sem verificacoes)
# Execute como: powershell -ExecutionPolicy Bypass -File quick_setup.ps1

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Setup Rapido - Sistema de Controle Financeiro" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

$success = "Green"
$errorColor = "Red"
$info = "Cyan"
$warning = "Yellow"

# 1. Criar ambiente virtual Python
Write-Host "[1/4] Criando ambiente virtual Python..." -ForegroundColor $info
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

# 2. Ativar ambiente virtual
Write-Host ""
Write-Host "[2/4] Ativando ambiente virtual..." -ForegroundColor $info
& ".\venv\Scripts\Activate.ps1"
Write-Host "   [OK] Ambiente virtual ativado" -ForegroundColor $success

# 3. Instalar dependencias Python
Write-Host ""
Write-Host "[3/4] Instalando dependencias Python..." -ForegroundColor $info
Write-Host "   [INFO] Atualizando pip e setuptools..." -ForegroundColor $info
python -m pip install --upgrade pip setuptools wheel --quiet
Write-Host "   [INFO] Instalando dependencias..." -ForegroundColor $info
pip install -r requirements.txt --no-build-isolation --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Dependencias Python instaladas" -ForegroundColor $success
} else {
    Write-Host "   [ERRO] Erro ao instalar dependencias Python" -ForegroundColor $errorColor
    exit 1
}

# 4. Instalar dependencias Frontend
Write-Host ""
Write-Host "[4/4] Instalando dependencias Frontend..." -ForegroundColor $info
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

# Criar arquivo .env se nao existir
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "[CONFIGURACAO] Criando arquivo .env..." -ForegroundColor $info
    Copy-Item ".env.example" ".env"
    Write-Host "   [OK] Arquivo .env criado" -ForegroundColor $success
}

# Resumo
Write-Host ""
Write-Host "===================================================================" -ForegroundColor $success
Write-Host "  [SUCESSO] SETUP CONCLUIDO!" -ForegroundColor $success
Write-Host "===================================================================" -ForegroundColor $success

Write-Host ""
Write-Host "[PROXIMOS PASSOS]" -ForegroundColor $info
Write-Host ""
Write-Host "1. Edite o arquivo .env com suas credenciais PostgreSQL:" -ForegroundColor $info
Write-Host "   notepad .env" -ForegroundColor $warning
Write-Host ""
Write-Host "2. Crie o banco de dados PostgreSQL:" -ForegroundColor $info
Write-Host "   powershell -ExecutionPolicy Bypass -File create_db.ps1" -ForegroundColor $warning
Write-Host ""
Write-Host "3. Inicie a aplicacao:" -ForegroundColor $info
Write-Host "   powershell -ExecutionPolicy Bypass -File start.ps1" -ForegroundColor $warning
Write-Host ""
