# Script para criar banco de dados PostgreSQL automaticamente
# Execute como: powershell -ExecutionPolicy Bypass -File create_db.ps1

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Criacao de Banco de Dados PostgreSQL" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

$success = "Green"
$errorColor = "Red"
$info = "Cyan"
$warning = "Yellow"

# Verificar se PostgreSQL esta instalado
Write-Host "[1/4] Verificando PostgreSQL..." -ForegroundColor $info
$psqlCheck = psql --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] PostgreSQL nao encontrado!" -ForegroundColor $errorColor
    Write-Host "Instale em: https://www.postgresql.org/" -ForegroundColor $warning
    exit 1
}
Write-Host "   [OK] PostgreSQL encontrado: $psqlCheck" -ForegroundColor $success

# Solicitar credenciais
Write-Host ""
Write-Host "[2/4] Configurando credenciais..." -ForegroundColor $info
$pgUser = Read-Host "   Usuario PostgreSQL (padrao: postgres)"
if ([string]::IsNullOrWhiteSpace($pgUser)) { $pgUser = "postgres" }

$pgPassword = Read-Host "   Senha PostgreSQL" -AsSecureString
$pgPasswordPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($pgPassword))

$pgHost = Read-Host "   Host PostgreSQL (padrao: localhost)"
if ([string]::IsNullOrWhiteSpace($pgHost)) { $pgHost = "localhost" }

$pgPort = Read-Host "   Porta PostgreSQL (padrao: 5432)"
if ([string]::IsNullOrWhiteSpace($pgPort)) { $pgPort = "5432" }

Write-Host ""
Write-Host "[3/4] Criando banco de dados..." -ForegroundColor $info

# Criar banco de dados
$env:PGPASSWORD = $pgPasswordPlain
psql -h $pgHost -p $pgPort -U $pgUser -tc "SELECT 1 FROM pg_database WHERE datname = 'financas_db'" | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "   [AVISO] Banco de dados ja existe" -ForegroundColor $warning
} else {
    psql -h $pgHost -p $pgPort -U $pgUser -c "CREATE DATABASE financas_db"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Banco de dados criado" -ForegroundColor $success
    } else {
        Write-Host "   [ERRO] Erro ao criar banco de dados" -ForegroundColor $errorColor
        exit 1
    }
}

# Atualizar arquivo .env
Write-Host ""
Write-Host "[4/4] Atualizando arquivo .env..." -ForegroundColor $info

$envContent = @"
DATABASE_URL=postgresql://$pgUser`:$pgPasswordPlain@$pgHost`:$pgPort/financas_db
JWT_SECRET_KEY=sua-chave-secreta-muito-segura-aqui-$(Get-Random)
FLASK_ENV=development
FLASK_DEBUG=True
"@

Set-Content -Path ".env" -Value $envContent
Write-Host "   [OK] Arquivo .env atualizado" -ForegroundColor $success

Write-Host ""
Write-Host "===================================================================" -ForegroundColor $success
Write-Host "  [SUCESSO] BANCO DE DADOS CRIADO COM SUCESSO!" -ForegroundColor $success
Write-Host "===================================================================" -ForegroundColor $success

Write-Host ""
Write-Host "[INFORMACOES DO BANCO DE DADOS]" -ForegroundColor $info
Write-Host "   Host:     $pgHost" -ForegroundColor $warning
Write-Host "   Porta:    $pgPort" -ForegroundColor $warning
Write-Host "   Usuario:  $pgUser" -ForegroundColor $warning
Write-Host "   Banco:    financas_db" -ForegroundColor $warning
Write-Host ""
Write-Host "[PROXIMOS PASSOS]" -ForegroundColor $info
Write-Host "1. Execute setup: powershell -ExecutionPolicy Bypass -File setup.ps1" -ForegroundColor $warning
Write-Host "2. Inicie a aplicacao: powershell -ExecutionPolicy Bypass -File start.ps1" -ForegroundColor $warning
Write-Host ""

# Limpar variavel de senha
Remove-Variable pgPasswordPlain
$env:PGPASSWORD = ""
