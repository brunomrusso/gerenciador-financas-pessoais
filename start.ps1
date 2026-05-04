# Script para iniciar Backend e Frontend simultaneamente
# Execute como: powershell -ExecutionPolicy Bypass -File start.ps1

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Iniciando Sistema de Controle Financeiro" -ForegroundColor Cyan
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

# Ativar ambiente virtual
Write-Host "[1/3] Ativando ambiente virtual Python..." -ForegroundColor $info
& ".\venv\Scripts\Activate.ps1"
Write-Host "[OK] Ambiente virtual ativado" -ForegroundColor $success

# Iniciar Backend em background
Write-Host ""
Write-Host "[2/3] Iniciando Backend (Flask)..." -ForegroundColor $info
$backendProcess = Start-Process -FilePath "python" -ArgumentList "run.py" -PassThru -NoNewWindow
Write-Host "[OK] Backend iniciado (PID: $($backendProcess.Id))" -ForegroundColor $success
Write-Host "[INFO] Backend em: http://localhost:5000" -ForegroundColor $warning

# Aguardar um pouco para o backend iniciar
Start-Sleep -Seconds 3

# Iniciar Frontend em background
Write-Host ""
Write-Host "[3/3] Iniciando Frontend (Svelte)..." -ForegroundColor $info
$frontendProcess = Start-Process -FilePath "npm" -ArgumentList "-C", "frontend", "run", "dev" -PassThru -NoNewWindow
Write-Host "[OK] Frontend iniciado (PID: $($frontendProcess.Id))" -ForegroundColor $success
Write-Host "[INFO] Frontend em: http://localhost:5173" -ForegroundColor $warning

# Aguardar um pouco para o frontend iniciar
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "===================================================================" -ForegroundColor $success
Write-Host "  [SUCESSO] APLICACAO INICIADA!" -ForegroundColor $success
Write-Host "===================================================================" -ForegroundColor $success

Write-Host ""
Write-Host "[STATUS]" -ForegroundColor $info
Write-Host "   Backend:  http://localhost:5000  (PID: $($backendProcess.Id))" -ForegroundColor $warning
Write-Host "   Frontend: http://localhost:5173  (PID: $($frontendProcess.Id))" -ForegroundColor $warning
Write-Host ""
Write-Host "[ACESSO] Abra no navegador: http://localhost:5173" -ForegroundColor $success
Write-Host ""
Write-Host "[PARAR] Para parar a aplicacao, feche esta janela ou pressione Ctrl+C" -ForegroundColor $warning
Write-Host ""

# Manter a janela aberta
Write-Host "Pressione Ctrl+C para parar..." -ForegroundColor $info
try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Verificar se os processos ainda estao rodando
        if (-not (Get-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host ""
            Write-Host "[AVISO] Backend foi encerrado" -ForegroundColor $warning
        }
        
        if (-not (Get-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host ""
            Write-Host "[AVISO] Frontend foi encerrado" -ForegroundColor $warning
        }
    }
} catch {
    Write-Host ""
    Write-Host "Encerrando processos..." -ForegroundColor $warning
    
    try {
        Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
        Write-Host "[OK] Backend encerrado" -ForegroundColor $success
    } catch {}
    
    try {
        Stop-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue
        Write-Host "[OK] Frontend encerrado" -ForegroundColor $success
    } catch {}
    
    Write-Host ""
    Write-Host "Ate logo!" -ForegroundColor $success
}
