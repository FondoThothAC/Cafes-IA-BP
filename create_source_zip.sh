#!/bin/bash

# Script para empaquetar SOLO CÓDIGO FUENTE
# Ideal para mover a otra máquina y hacer install limpio

echo "📦 Creando paquete ligero (Source Only)..."
DATE=$(date +%Y%m%d)
FILENAME="Plania_Source_v3_$DATE.zip"

# Limpiar archivos basura
# Crear carpeta temporal para limpiar rutas (Staging)
rm -rf staging_build
mkdir -p staging_build

echo "📂 Copiando archivos base..."
cp docker-compose.yml staging_build/
cp install-windows.ps1 staging_build/
cp install.bat staging_build/
cp .env.example staging_build/
cp README.md staging_build/
cp -r services staging_build/

echo "📂 Copiando PlanIA..."
mkdir -p staging_build/PlanIA
# Copiar contenido de PlanIA excluyendo basura
rsync -av --exclude 'node_modules' --exclude '.git' --exclude '.DS_Store' \
    "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/Plan A/PlanIA/" \
    staging_build/PlanIA/

echo "📂 Copiando CAFES..."
mkdir -p staging_build/CAFES
# Copiar contenido de CAFES excluyendo basura
rsync -av --exclude 'node_modules' --exclude '.git' --exclude '.DS_Store' \
    "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/PlanIA-CAFES/" \
    staging_build/CAFES/

echo "🗜️  Comprimiendo..."
cd staging_build
zip -r "../$FILENAME" .
cd ..
rm -rf staging_build

echo ""
echo "✅ Paquete generado: $FILENAME"
echo "📂 Tamaño:"
du -h "$FILENAME"
echo ""
echo "Instrucciones para HP (Windows):"
echo "1. Copia $FILENAME a la HP"
echo "2. Descomprime"
echo "3. Ejecuta install-windows.ps1 (Administrador)"
