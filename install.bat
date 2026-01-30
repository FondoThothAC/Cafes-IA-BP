@echo off
TITLE Instalador AI-Toolkit (PlanIA)
COLOR 0A

echo ===================================================
echo   INICIANDO INSTALADOR AUTOMATICO AI-TOOLKIT
echo ===================================================
echo.
echo   Este script instalara Docker, Drivers y configurara
echo   todo el entorno automaticamente.
echo.
echo   Solicitando permisos de Administrador...
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo   [OK] Permisos concedidos.
) else (
    echo   [ERROR] Necesitas ejecutar como Administrador.
    echo   Haz clic derecho en este archivo y elige "Ejecutar como administrador".
    pause
    exit
)

echo.
echo   Ejecutando script de instalacion inteligente...
echo.

:: Ejecutar PowerShell con política Bypass para evitar restricciones
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-windows.ps1"

if %errorLevel% neq 0 (
    echo.
    echo   [HUBO UN ERROR] El script de instalacion fallo.
    pause
) else (
    echo.
    echo   [FINALIZADO] Puedes cerrar esta ventana.
    pause
)
