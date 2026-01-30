# ============================================
# AI-Toolkit: Instalador Automatico
# ============================================

# Forzar ejecucion en el directorio del script
Set-Location $PSScriptRoot

# --- MIGRACION A CARPETA FIJA ---
$TargetDir = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "Proyecto IA Tools"

if ($PWD.Path -ne $TargetDir) {
    Write-Host ">>> Instalacion detectada en carpeta temporal." -ForegroundColor Yellow
    Write-Host ">>> Moviendo proyecto a: $TargetDir" -ForegroundColor Cyan
    
    if (-not (Test-Path $TargetDir)) { New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null }
    
    # Copiar todo (Sobreescribir)
    Copy-Item -Path "$PSScriptRoot\*" -Destination $TargetDir -Recurse -Force
    
    Write-Host ">>> Reiniciando desde nueva ubicacion..." -ForegroundColor Green
    Start-Sleep -Seconds 2
    
    # Relanzar script como Admin desde la nueva carpeta
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$TargetDir\install-windows.ps1`"" -Verb RunAs
    exit
}
# --------------------------------

Write-Host ">>> Iniciando Instalacion Inteligente AI-Toolkit..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# 1. Verificar Permisos de Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ADVERTENCIA] Por favor, ejecuta este archivo como ADMINISTRADOR." -ForegroundColor Yellow
    Write-Host "   (Clic derecho > Ejecutar con PowerShell)"
    pause
    exit 1
}

# 2. Funcion para Instalar con Winget
function Install-WithWinget ($id, $name) {
    Write-Host "... Instalando $name..." -ForegroundColor Cyan
    winget install -e --id $id --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $name instalado correctamente." -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Error instalando $name." -ForegroundColor Red
    }
}

# 3. Comprobaciones e Instalaciones
Write-Host "`n>>> Analizando sistema..." -ForegroundColor Yellow

# --- WSL2 ---
$wslStatus = wsl --status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FALTA] WSL2 no detectado. Instalando..." -ForegroundColor Yellow
    wsl --install
    Write-Host "[REINICIO] Es necesario REINICIAR Windows para activar WSL2." -ForegroundColor Red
    Write-Host "   Por favor reinicia y vuelve a ejecutar este script."
    pause
    exit 1
} else {
    Write-Host "[OK] WSL2: Instalado" -ForegroundColor Green
}

# --- Docker Desktop ---
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[FALTA] Docker no detectado. Instalando via Winget..." -ForegroundColor Yellow
    Install-WithWinget "Docker.DockerDesktop" "Docker Desktop"
    Write-Host "[INFO] Docker instalado. Iniciando..." 
    & "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "Waiting for Docker (30s)..."
    Start-Sleep -Seconds 30
} else {
    Write-Host "[OK] Docker: Instalado" -ForegroundColor Green
    if (!(docker info 2>&1 | Select-String "Server Version")) {
        Write-Host ">>> Iniciando Docker Desktop..." -ForegroundColor Cyan
        & "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        Start-Sleep -Seconds 15
    }
}

# --- NVIDIA Driver ---
if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
    Write-Host "[FALTA] Drivers NVIDIA no detectados. Intentando instalar..." -ForegroundColor Yellow
    Install-WithWinget "Nvidia.DisplayDriver" "NVIDIA Drivers"
} else {
    $gpuParams = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    Write-Host "[OK] GPU Detectada: $gpuParams" -ForegroundColor Green
}

# --- Git ---
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[INFO] Instalando Git..." -ForegroundColor Gray
    Install-WithWinget "Git.Git" "Git"
}

# 4. Configuracion del Proyecto
Write-Host "`n>>> Configuracion de carpetas..." -ForegroundColor Yellow
$folders = @("data\models", "data\knowledge_base", "data\whatsapp-session", "mysql_data", "data\moltbot")
foreach ($f in $folders) {
    if (-not (Test-Path $f)) { New-Item -ItemType Directory -Path $f -Force | Out-Null }
}

# 5. Configurar Variables (.env)
if (-not (Test-Path ".env")) {
    Write-Host "[CONFIG] Generando configuracion..."
    Copy-Item ".env.example" ".env"
    
    # Preguntar Token
    $token = Read-Host "`n>>> Pega tu TELEGRAM_BOT_TOKEN (Enter para omitir)"
    if ($token) {
        (Get-Content ".env") -replace "TELEGRAM_BOT_TOKEN=.*", "TELEGRAM_BOT_TOKEN=$token" | Set-Content ".env"
    }
    
    # Ajuste GPU
    Add-Content ".env" "`nPLATFORM=windows`nGPU_ENABLED=true`nOLLAMA_MODEL=qwen2.5:14b"
}

# 6. Despliegue
Write-Host "`n>>> Desplegando Contenedores..." -ForegroundColor Cyan

if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "[ERROR FATAL] No se encuentra docker-compose.yml en: $PWD" -ForegroundColor Red
    pause
    exit 1
}

docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[EXITO] INSTALACION COMPLETADA!" -ForegroundColor Green
    Write-Host "   - Telegram Bot: Activo"
    Write-Host "   - WhatsApp Bot: Revisa logs para QR"
    Write-Host "   - PlanIA Web: Copiado en esta carpeta"
} else {
    Write-Host "[ERROR] en el despliegue de Docker." -ForegroundColor Red
}

pause
