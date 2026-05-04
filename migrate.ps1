# Script para migrar dados do Excel para PostgreSQL
# Execute como: powershell -ExecutionPolicy Bypass -File migrate.ps1

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         🔄 Migração de Dados - Excel para PostgreSQL          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$success = "Green"
$errorColor = "Red"
$info = "Cyan"
$warning = "Yellow"

# Verificar se .env existe
if (-not (Test-Path ".env")) {
    Write-Host "❌ Arquivo .env não encontrado!" -ForegroundColor $errorColor
    Write-Host "Execute primeiro: powershell -ExecutionPolicy Bypass -File setup.ps1" -ForegroundColor $warning
    exit 1
}

# Verificar se arquivo Excel existe
if (-not (Test-Path "controle_financeiro.xlsx")) {
    Write-Host "❌ Arquivo controle_financeiro.xlsx não encontrado!" -ForegroundColor $errorColor
    Write-Host "Coloque o arquivo na pasta raiz do projeto" -ForegroundColor $warning
    exit 1
}

Write-Host "1️⃣  Ativando ambiente virtual Python..." -ForegroundColor $info
& ".\venv\Scripts\Activate.ps1"
Write-Host "   ✅ Ambiente virtual ativado" -ForegroundColor $success

Write-Host ""
Write-Host "2️⃣  Iniciando migração de dados..." -ForegroundColor $info
Write-Host "   ⏳ Isso pode levar alguns minutos..." -ForegroundColor $warning
Write-Host ""

python migrate_data.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor $success
    Write-Host "║                  ✅ MIGRAÇÃO CONCLUÍDA!                       ║" -ForegroundColor $success
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor $success
    Write-Host ""
    Write-Host "📊 Dados migrados com sucesso!" -ForegroundColor $success
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor $info
    Write-Host "1. Inicie a aplicação: powershell -ExecutionPolicy Bypass -File start.ps1" -ForegroundColor $warning
    Write-Host "2. Faça login com: admin@financas.local / admin123" -ForegroundColor $warning
    Write-Host "3. Seus dados históricos estarão disponíveis" -ForegroundColor $warning
} else {
    Write-Host ""
    Write-Host "❌ Erro durante a migração!" -ForegroundColor $errorColor
    Write-Host "Verifique o arquivo .env e tente novamente" -ForegroundColor $warning
    exit 1
}
