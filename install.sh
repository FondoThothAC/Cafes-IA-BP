#!/bin/bash
# ============================================
# AI-Toolkit: Mac Installer (Apple Silicon)
# ============================================
# Detecta M1/M2/M3/M4, ofrece MLX o Ollama,
# y configura el modelo óptimo
# ============================================

set -e

echo "🚀 AI-Toolkit Mac Installer"
echo "============================"

# ============================================
# 1. Detectar arquitectura
# ============================================
ARCH=$(uname -m)
echo ""
echo "🔍 Detectando hardware..."

if [[ "$ARCH" == "arm64" ]]; then
    echo "✅ Apple Silicon detectado ($ARCH)"
    CHIP="apple_silicon"
else
    echo "⚠️  Intel Mac detectado - rendimiento limitado"
    CHIP="intel"
fi

# Detectar RAM
RAM_GB=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
echo "   RAM: ${RAM_GB}GB"

# ============================================
# 2. Preguntar backend preferido
# ============================================
echo ""
echo "🧠 Selecciona el backend de IA:"
echo ""
echo "   1) Ollama (Docker) - Estándar, portable"
echo "   2) MLX (Nativo) - Máximo rendimiento en Mac"
echo "   3) Ambos - Ollama por defecto, MLX disponible"
echo ""
read -p "Opción [1/2/3] (default: 1): " BACKEND_CHOICE
BACKEND_CHOICE=${BACKEND_CHOICE:-1}

case $BACKEND_CHOICE in
    1)
        BACKEND="ollama"
        echo "✅ Usando Ollama (Docker)"
        ;;
    2)
        BACKEND="mlx"
        echo "✅ Usando MLX (Nativo)"
        ;;
    3)
        BACKEND="both"
        echo "✅ Instalando ambos (Ollama + MLX)"
        ;;
    *)
        BACKEND="ollama"
        echo "✅ Usando Ollama (Docker) por defecto"
        ;;
esac

# ============================================
# 3. Seleccionar modelo
# ============================================
echo ""
echo "📦 Selecciona el modelo principal:"
echo ""

if [[ $RAM_GB -ge 32 ]]; then
    echo "   1) gemma3n:4b    - Multimodal, rápido (2.5GB)"
    echo "   2) qwen2.5:7b    - Mejor español (4.5GB)"
    echo "   3) deepseek-r1:14b - Razonamiento (9GB)"
    echo "   4) llava:13b     - Análisis visual (8GB)"
    DEFAULT_MODEL="2"
elif [[ $RAM_GB -ge 16 ]]; then
    echo "   1) gemma3n:4b    - Multimodal, rápido (2.5GB) ⭐"
    echo "   2) qwen2.5:7b    - Mejor español (4.5GB)"
    echo "   3) deepseek-r1:7b - Razonamiento (4.5GB)"
    echo "   4) llama3.2:3b   - Ligero (2GB)"
    DEFAULT_MODEL="1"
else
    echo "   1) gemma3:1b     - Ultra ligero (600MB)"
    echo "   2) gemma3n:4b    - Multimodal (2.5GB)"
    echo "   3) phi-4:3b      - Compacto (2.2GB)"
    DEFAULT_MODEL="1"
fi

echo ""
read -p "Opción (default: $DEFAULT_MODEL): " MODEL_CHOICE
MODEL_CHOICE=${MODEL_CHOICE:-$DEFAULT_MODEL}

case $MODEL_CHOICE in
    1) 
        if [[ $RAM_GB -ge 16 ]]; then
            MODEL="gemma3n:4b"
        else
            MODEL="gemma3:1b"
        fi
        ;;
    2) 
        if [[ $RAM_GB -ge 16 ]]; then
            MODEL="qwen2.5:7b"
        else
            MODEL="gemma3n:4b"
        fi
        ;;
    3) 
        if [[ $RAM_GB -ge 32 ]]; then
            MODEL="deepseek-r1:14b"
        elif [[ $RAM_GB -ge 16 ]]; then
            MODEL="deepseek-r1:7b"
        else
            MODEL="phi-4:3b"
        fi
        ;;
    4) 
        if [[ $RAM_GB -ge 16 ]]; then
            MODEL="llava:13b"
        else
            MODEL="llama3.2:3b"
        fi
        ;;
    *)
        MODEL="gemma3n:4b"
        ;;
esac

echo "✅ Modelo seleccionado: $MODEL"

# ============================================
# 4. Guardar configuración
# ============================================
cat > .env << EOF
# AI-Toolkit: Mac Configuration
# ==============================
# Generated: $(date)

# Hardware
PLATFORM=mac
CHIP=$CHIP
RAM_GB=$RAM_GB

# Backend
BACKEND=$BACKEND

# Modelo principal
OLLAMA_MODEL=$MODEL

# Modelos adicionales sugeridos
REASONING_MODEL=deepseek-r1:7b
VISION_MODEL=llava:7b

# Whisper
WHISPER_MODEL=base

# Puertos
OLLAMA_PORT=11434
WHISPER_PORT=9000
GATEWAY_PORT=3002

# MLX (si está habilitado)
MLX_ENABLED=$([[ "$BACKEND" == "mlx" || "$BACKEND" == "both" ]] && echo "true" || echo "false")
MLX_MODEL=mlx-community/gemma-3-4b-it-4bit
EOF

echo "✅ Configuración guardada en .env"

# ============================================
# 5. Instalar según backend
# ============================================
echo ""
echo "📁 Creando estructura de datos..."
mkdir -p data/models data/knowledge_base data/transcriptions data/moltbot

if [[ "$BACKEND" == "ollama" || "$BACKEND" == "both" ]]; then
    echo ""
    echo "🐳 Verificando Docker..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker no está instalado."
        echo "   Instálalo desde: https://www.docker.com/products/docker-desktop/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo "⚠️  Docker no está corriendo. Iniciando..."
        open -a Docker
        echo "   Espera a que Docker inicie y vuelve a ejecutar el script"
        exit 1
    fi
    
    echo "✅ Docker disponible"
    echo ""
    echo "🐳 Iniciando contenedores..."
    docker compose up -d --build
    
    echo ""
    echo "⏳ Esperando a que Ollama esté listo..."
    sleep 15
    
    echo ""
    echo "📦 Descargando modelo $MODEL..."
    docker exec ai-ollama ollama pull $MODEL
fi

if [[ "$BACKEND" == "mlx" || "$BACKEND" == "both" ]]; then
    echo ""
    echo "🍎 Instalando MLX..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 no encontrado"
        exit 1
    fi
    
    # Instalar MLX
    pip3 install --upgrade mlx-lm huggingface_hub
    
    echo ""
    echo "📦 Descargando modelo MLX..."
    python3 -c "from huggingface_hub import snapshot_download; snapshot_download('mlx-community/gemma-3-4b-it-4bit', local_dir='data/mlx-models/gemma-3-4b')"
    
    echo "✅ MLX instalado"
fi

# ============================================
# 6. Resumen final
# ============================================
echo ""
echo "============================================"
echo "✅ ¡AI-Toolkit instalado correctamente!"
echo "============================================"
echo ""
echo "📍 Servicios disponibles:"

if [[ "$BACKEND" == "ollama" || "$BACKEND" == "both" ]]; then
    echo "   • Ollama API: http://localhost:11434"
    echo "   • Whisper API: http://localhost:9000"
    echo "   • Gateway API: http://localhost:3002"
    echo "   • Model Manager: http://localhost:3002/models"
fi

if [[ "$BACKEND" == "mlx" || "$BACKEND" == "both" ]]; then
    echo ""
    echo "🍎 MLX disponible:"
    echo "   python3 -m mlx_lm.generate --model data/mlx-models/gemma-3-4b --prompt 'Hola'"
fi

echo ""
echo "📦 Modelo activo: $MODEL"
echo ""
