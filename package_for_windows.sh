#!/bin/bash

# Script para empaquetar AI-Toolkit para Windows (HP RTX)
# Excluye node_modules y carpetas de datos pesadas

echo "📦 Preparando paquete AI-Toolkit para Windows..."

# Nombre del archivo
DATE=$(date +%Y%m%d)
FILENAME="AI-Toolkit_Windows_$DATE.zip"

# Limpiar archivos temporales (.DS_Store, etc)
find . -name ".DS_Store" -delete

# COPIAR PLANIA (Web App)
echo "📂 Integrando PlanIA Web..."
mkdir -p services/plania
# Copy from relative path (Assuming standard dev structure) or prompt user?
# For now, hardcode the known user path or expect it nearby.
# Better: Use the absolute path we know from this session:
SOURCE_PLANIA="/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/Plan A/PlanIA"
if [ -d "$SOURCE_PLANIA" ]; then
    rsync -av --progress "$SOURCE_PLANIA/" "services/plania/" --exclude '.git' --exclude 'node_modules'
else
    echo "⚠️ ADVERTENCIA: No se encontró PlanIA en $SOURCE_PLANIA. El ZIP solo tendrá la infraestructura AI."
fi

# Crear ZIP excluyendo carpetas pesadas
echo "🗜️  Comprimiendo..."
zip -r "$FILENAME" . \
    -x "**/node_modules/*" \
    -x "**/data/models/*" \
    -x "**/data/knowledge_base/*" \
    -x "**/data/transcriptions/*" \
    -x "**/data/moltbot/*" \
    -x "**/data/whatsapp-session/*" \
    -x "**/mysql_data/*" \
    -x "**/whatsapp_data/*" \
    -x "**/.git/*" \
    -x "**/.env" 

echo "✅ Paquete creado: $FILENAME"
echo "👉 Copia este archivo a tu HP con Windows y descomprímelo."
echo "👉 Luego ejecuta 'install-windows.ps1' como Administrador."
