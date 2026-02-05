#!/bin/bash
# =================================================================================
# PROYECTO: PlanIA - Auto Start Script
# DESCRIPCIÓN: Inicia todos los servicios (DB, Backend, Scraper, OCR, Agente)
# =================================================================================

echo "🚀 Iniciando PlanIA System..."

# 1. Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
  echo "❌ Error: Docker no está corriendo. Por favor inicia Docker Desktop primero."
  exit 1
fi

# 2. Construir e iniciar contenedores
echo "🐳 Construyendo e iniciando contenedores..."
docker-compose up --build -d

# 3. Esperar a que los servicios estén listos (simple wait)
echo "⏳ Esperando a que los servicios inicialicen (10s)..."
sleep 10

# 4. Mostrar estado
echo "✅ Servicios activos:"
docker-compose ps

echo ""
echo "📱 Frontend Wizard: http://localhost:8080/wizard.html"
echo "🤖 Agente API:      http://localhost:5000/health"
echo "🕷️ Web Scraper:     http://localhost:3005"
echo "👁️ OCR Service:     http://localhost:5001/health"
echo ""
echo "Para detener todo, ejecuta: docker-compose down"
