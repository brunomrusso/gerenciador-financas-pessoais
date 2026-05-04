# Inicia apenas o Frontend Svelte
# Execute: powershell -ExecutionPolicy Bypass -File start_frontend.ps1

Write-Host "Iniciando Frontend Svelte..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:5173" -ForegroundColor Yellow
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

Push-Location "frontend"
npm run dev
Pop-Location
