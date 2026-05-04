# Script para criar banco de dados PostgreSQL
# Nao requer psql no PATH - usa Python/psycopg2
# Execute como: powershell -ExecutionPolicy Bypass -File create_db.ps1

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Criacao de Banco de Dados PostgreSQL" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

$success = "Green"
$errorColor = "Red"
$info = "Cyan"
$warning = "Yellow"

# Ativar ambiente virtual (necessario para psycopg2)
if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "[ERRO] Ambiente virtual nao encontrado!" -ForegroundColor $errorColor
    Write-Host "Execute primeiro: powershell -ExecutionPolicy Bypass -File quick_setup.ps1" -ForegroundColor $warning
    exit 1
}

$pythonExe = ".\venv\Scripts\python.exe"

# Solicitar credenciais
Write-Host "[1/3] Configurando credenciais do PostgreSQL..." -ForegroundColor $info
Write-Host ""

$pgHost = Read-Host "   Host (padrao: localhost)"
if ([string]::IsNullOrWhiteSpace($pgHost)) { $pgHost = "localhost" }

$pgPort = Read-Host "   Porta (padrao: 5432)"
if ([string]::IsNullOrWhiteSpace($pgPort)) { $pgPort = "5432" }

$pgUser = Read-Host "   Usuario (padrao: postgres)"
if ([string]::IsNullOrWhiteSpace($pgUser)) { $pgUser = "postgres" }

$pgPassword = Read-Host "   Senha" -AsSecureString
$pgPasswordPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($pgPassword)
)

# Criar banco de dados usando Python
Write-Host ""
Write-Host "[2/3] Criando banco de dados 'financas_db'..." -ForegroundColor $info
& $pythonExe "create_db_helper.py" $pgHost $pgPort $pgUser $pgPasswordPlain

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERRO] Falha ao criar banco de dados." -ForegroundColor $errorColor
    Write-Host "Verifique se:" -ForegroundColor $warning
    Write-Host "  - PostgreSQL esta rodando" -ForegroundColor $warning
    Write-Host "  - Host, porta, usuario e senha estao corretos" -ForegroundColor $warning
    exit 1
}

# Salvar credenciais no .env
Write-Host ""
Write-Host "[3/3] Salvando configuracao no arquivo .env..." -ForegroundColor $info

$jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 40 | ForEach-Object { [char]$_ })

$envContent = @"
DATABASE_URL=postgresql://$pgUser`:$pgPasswordPlain@$pgHost`:$pgPort/financas_db
JWT_SECRET_KEY=$jwtSecret
FLASK_ENV=development
FLASK_DEBUG=True
"@

Set-Content -Path ".env" -Value $envContent -Encoding UTF8
Write-Host "   [OK] Arquivo .env atualizado" -ForegroundColor $success

# Limpar senha da memoria
$pgPasswordPlain = $null
[System.GC]::Collect()

Write-Host ""
Write-Host "===================================================================" -ForegroundColor $success
Write-Host "  [SUCESSO] CONFIGURACAO CONCLUIDA!" -ForegroundColor $success
Write-Host "===================================================================" -ForegroundColor $success
Write-Host ""
Write-Host "[PROXIMO PASSO] Inicie a aplicacao:" -ForegroundColor $info
Write-Host "  powershell -ExecutionPolicy Bypass -File start.ps1" -ForegroundColor $warning
Write-Host ""
