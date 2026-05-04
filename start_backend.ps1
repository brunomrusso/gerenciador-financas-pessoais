# Inicia apenas o Backend Flask
# Execute: powershell -ExecutionPolicy Bypass -File start_backend.ps1

Write-Host "Iniciando Backend Flask..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:5000" -ForegroundColor Yellow
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

& ".\venv\Scripts\python.exe" run.py
