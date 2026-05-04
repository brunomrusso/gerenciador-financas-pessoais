# Script Master de Instalação Completa
# Execute como: powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      🚀 INSTALAÇÃO COMPLETA - Sistema de Controle Financeiro  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$success = "Green"
$errorColor = "Red"
$info = "Cyan"
$warning = "Yellow"

# Menu de opções
Write-Host "Escolha uma opção:" -ForegroundColor $info
Write-Host ""
Write-Host "1. Instalação Completa (Recomendado)" -ForegroundColor $warning
Write-Host "   └─ Setup + Criar BD + Migrar dados + Iniciar"
Write-Host ""
Write-Host "2. Apenas Setup" -ForegroundColor $warning
Write-Host "   └─ Instalar dependências"
Write-Host ""
Write-Host "3. Criar Banco de Dados" -ForegroundColor $warning
Write-Host "   └─ Criar BD PostgreSQL"
Write-Host ""
Write-Host "4. Migrar Dados" -ForegroundColor $warning
Write-Host "   └─ Importar dados do Excel"
Write-Host ""
Write-Host "5. Iniciar Aplicação" -ForegroundColor $warning
Write-Host "   └─ Rodar Backend + Frontend"
Write-Host ""

$choice = Read-Host "Digite sua escolha (1-5)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Executando instalação completa..." -ForegroundColor $info
        
        # Setup
        Write-Host ""
        Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor $info
        Write-Host "ETAPA 1: Setup" -ForegroundColor $info
        Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor $info
        & ".\setup.ps1"
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Erro no setup" -ForegroundColor $errorColor
            exit 1
        }
        
        # Criar BD
        Write-Host ""
        Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor $info
        Write-Host "ETAPA 2: Criar Banco de Dados" -ForegroundColor $info
        Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor $info
        & ".\create_db.ps1"
        
        # Migrar dados
        $migrar = Read-Host ""
        Write-Host ""
        Write-Host "Deseja migrar dados do Excel? (S/N)"
        $migrar = Read-Host
        
        if ($migrar -eq "S" -or $migrar -eq "s") {
            Write-Host ""
            Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor $info
            Write-Host "ETAPA 3: Migração de Dados" -ForegroundColor $info
            Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor $info
            & ".\migrate.ps1"
        }
        
        # Iniciar
        Write-Host ""
        Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor $info
        Write-Host "ETAPA 4: Iniciar Aplicação" -ForegroundColor $info
        Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor $info
        & ".\start.ps1"
    }
    
    "2" {
        Write-Host ""
        & ".\setup.ps1"
    }
    
    "3" {
        Write-Host ""
        & ".\create_db.ps1"
    }
    
    "4" {
        Write-Host ""
        & ".\migrate.ps1"
    }
    
    "5" {
        Write-Host ""
        & ".\start.ps1"
    }
    
    default {
        Write-Host "❌ Opção inválida!" -ForegroundColor $errorColor
        exit 1
    }
}
