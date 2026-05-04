# Script para iniciar Backend e Frontend simultaneamente
# Execute como: powershell -ExecutionPolicy Bypass -File start.ps1

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        🚀 Iniciando Sistema de Controle Financeiro            ║" -ForegroundColor Cyan
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

# Ativar ambiente virtual
Write-Host "1️⃣  Ativando ambiente virtual Python..." -ForegroundColor $info
& ".\venv\Scripts\Activate.ps1"
Write-Host "   ✅ Ambiente virtual ativado" -ForegroundColor $success

# Iniciar Backend em background
Write-Host ""
Write-Host "2️⃣  Iniciando Backend (Flask)..." -ForegroundColor $info
$backendProcess = Start-Process -FilePath "python" -ArgumentList "run.py" -PassThru -NoNewWindow
Write-Host "   ✅ Backend iniciado (PID: $($backendProcess.Id))" -ForegroundColor $success
Write-Host "   📍 Backend em: http://localhost:5000" -ForegroundColor $warning

# Aguardar um pouco para o backend iniciar
Start-Sleep -Seconds 3

# Iniciar Frontend em background
Write-Host ""
Write-Host "3️⃣  Iniciando Frontend (Svelte)..." -ForegroundColor $info
$frontendProcess = Start-Process -FilePath "npm" -ArgumentList "-C", "frontend", "run", "dev" -PassThru -NoNewWindow
Write-Host "   ✅ Frontend iniciado (PID: $($frontendProcess.Id))" -ForegroundColor $success
Write-Host "   📍 Frontend em: http://localhost:5173" -ForegroundColor $warning

# Aguardar um pouco para o frontend iniciar
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor $success
Write-Host "║                  ✅ APLICAÇÃO INICIADA!                       ║" -ForegroundColor $success
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor $success

Write-Host ""
Write-Host "📊 Status:" -ForegroundColor $info
Write-Host "   Backend:  http://localhost:5000  (PID: $($backendProcess.Id))" -ForegroundColor $warning
Write-Host "   Frontend: http://localhost:5173  (PID: $($frontendProcess.Id))" -ForegroundColor $warning
Write-Host ""
Write-Host "🌐 Abra no navegador: http://localhost:5173" -ForegroundColor $success
Write-Host ""
Write-Host "⏹️  Para parar a aplicação, feche esta janela ou pressione Ctrl+C" -ForegroundColor $warning
Write-Host ""

# Manter a janela aberta
Write-Host "Pressione Ctrl+C para parar..." -ForegroundColor $info
try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Verificar se os processos ainda estão rodando
        if (-not (Get-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host ""
            Write-Host "⚠️  Backend foi encerrado" -ForegroundColor $warning
        }
        
        if (-not (Get-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host ""
            Write-Host "⚠️  Frontend foi encerrado" -ForegroundColor $warning
        }
    }
} catch {
    Write-Host ""
    Write-Host "Encerrando processos..." -ForegroundColor $warning
    
    try {
        Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
        Write-Host "✅ Backend encerrado" -ForegroundColor $success
    } catch {}
    
    try {
        Stop-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue
        Write-Host "✅ Frontend encerrado" -ForegroundColor $success
    } catch {}
    
    Write-Host ""
    Write-Host "Até logo! 👋" -ForegroundColor $success
}
