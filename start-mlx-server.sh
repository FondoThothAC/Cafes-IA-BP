#!/bin/bash
# ============================================
# MLX Server - Gemma 3 4B Multimodal
# ============================================
# Inicia servidor MLX con API compatible OpenAI
# Puerto: 8000
# ============================================

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuración
MODEL_PATH="$HOME/.cache/mlx-models/gemma-3-4b-it"
MODEL_HF="mlx-community/gemma-3-4b-it-qat-4bit"
PORT=8000

echo -e "${BLUE}🤖 MLX Server - Gemma 3 4B Multimodal${NC}"
echo "========================================"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado"
    exit 1
fi

# Verificar mlx-lm
if ! python3 -c "import mlx_lm" 2>/dev/null; then
    echo "📦 Instalando mlx-lm..."
    pip3 install mlx-lm --user
fi

# Verificar modelo
if [ ! -d "$MODEL_PATH" ]; then
    echo "📥 Descargando modelo Gemma 3 4B..."
    python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('$MODEL_HF', local_dir='$MODEL_PATH')
"
fi

echo -e "${GREEN}✅ Modelo listo: $MODEL_PATH${NC}"
echo -e "${BLUE}🚀 Iniciando servidor en puerto $PORT...${NC}"

# Iniciar servidor MLX
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
python3 -m mlx_lm.server \
    --model "$MODEL_PATH" \
    --host 0.0.0.0 \
    --port $PORT

# Alternativa si falla
# mlx_lm.server --model "$MODEL_HF" --host 0.0.0.0 --port $PORT
