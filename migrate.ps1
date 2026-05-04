# Script para migrar dados do Excel para PostgreSQL
# Execute como: powershell -ExecutionPolicy Bypass -File migrate.ps1

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Migracao de Dados - Excel para PostgreSQL" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

$success = "Green"
$errorColor = "Red"
$info = "Cyan"
$warning = "Yellow"

# Verificar se .env existe
if (-not (Test-Path ".env")) {
    Write-Host "[ERRO] Arquivo .env nao encontrado!" -ForegroundColor $errorColor
    Write-Host "Execute primeiro: powershell -ExecutionPolicy Bypass -File setup.ps1" -ForegroundColor $warning
    exit 1
}

# Verificar se arquivo Excel existe
if (-not (Test-Path "controle_financeiro.xlsx")) {
    Write-Host "[ERRO] Arquivo controle_financeiro.xlsx nao encontrado!" -ForegroundColor $errorColor
    Write-Host "Coloque o arquivo na pasta raiz do projeto" -ForegroundColor $warning
    exit 1
}

Write-Host "[1/2] Ativando ambiente virtual Python..." -ForegroundColor $info
& ".\venv\Scripts\Activate.ps1"
Write-Host "   [OK] Ambiente virtual ativado" -ForegroundColor $success

Write-Host ""
Write-Host "[2/2] Iniciando migracao de dados..." -ForegroundColor $info
Write-Host "   [INFO] Isso pode levar alguns minutos..." -ForegroundColor $warning
Write-Host ""

python migrate_data.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "===================================================================" -ForegroundColor $success
    Write-Host "  [SUCESSO] MIGRACAO CONCLUIDA!" -ForegroundColor $success
    Write-Host "===================================================================" -ForegroundColor $success
    Write-Host ""
    Write-Host "[RESULTADO] Dados migrados com sucesso!" -ForegroundColor $success
    Write-Host ""
    Write-Host "[PROXIMOS PASSOS]" -ForegroundColor $info
    Write-Host "1. Inicie a aplicacao: powershell -ExecutionPolicy Bypass -File start.ps1" -ForegroundColor $warning
    Write-Host "2. Faca login com: admin@financas.local / admin123" -ForegroundColor $warning
    Write-Host "3. Seus dados historicos estarao disponiveis" -ForegroundColor $warning
} else {
    Write-Host ""
    Write-Host "[ERRO] Erro durante a migracao!" -ForegroundColor $errorColor
    Write-Host "Verifique o arquivo .env e tente novamente" -ForegroundColor $warning
    exit 1
}
