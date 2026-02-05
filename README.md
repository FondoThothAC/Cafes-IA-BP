# 🤖 AI-Toolkit

Sistema de IA local containerizado. 100% aislado, portable entre Mac y Windows.

## 🚀 Instalación Rápida

### Mac (Apple Silicon)
```bash
cd AI-Toolkit
chmod +x install.sh
./install.sh
```

### Windows (NVIDIA GPU)
```powershell
cd AI-Toolkit
.\install-windows.ps1
```

## 📦 Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Ollama | 11434 | Modelos de IA |
| Whisper | 9000 | Transcripción audio |
| Gateway | 3002 | API unificada |
| **Model Manager** | 3002/models | **UI para gestionar modelos** |

## 🎯 Modelos Predeterminados

| Plataforma | Modelo | Características |
|------------|--------|-----------------|
| **Mac (16GB)** | gemma3n:4b | Multimodal, rápido |
| **Windows RTX** | qwen2.5:14b | Potente, español |

## 🖥️ Model Manager

Accede a `http://localhost:3002/models` para:
- Ver modelos instalados
- Descargar nuevos modelos
- Cambiar modelo activo
- Ver estadísticas del sistema

## 🔧 Comandos Útiles

```bash
# Iniciar
docker compose up -d

# Ver logs
docker compose logs -f

# Añadir modelo
docker exec ai-ollama ollama pull deepseek-r1:7b

# Listar modelos
docker exec ai-ollama ollama list

# Detener
docker compose down
```

## 🍎 MLX (Mac Nativo)

Si elegiste MLX en la instalación:
```bash
# Generar texto
python3 -m mlx_lm.generate \
  --model data/mlx-models/gemma-3-4b \
  --prompt "Analiza este plan de negocios:"

# Chat interactivo
python3 -m mlx_lm.chat --model data/mlx-models/gemma-3-4b
```

## 🦞 Activar Moltbot + OSINT

1. Editar `docker-compose.yml`
2. Descomentar sección `moltbot:`
3. Ejecutar:
```bash
docker compose up -d --build moltbot
```

## 📁 Estructura de Datos

```
data/
├── models/           # Modelos Ollama
├── knowledge_base/   # PDFs, TXTs, URLs
├── transcriptions/   # Audios transcritos
└── moltbot/          # Datos de Moltbot
```

## 🔒 Seguridad

- ✅ Contenedores solo ven `data/`
- ✅ Sin acceso a archivos personales
- ✅ 100% local (sin envío a cloud)
- ✅ Portable entre máquinas

## 📜 Licencia y Estado

- **Licencia**: GPL v2 (Versión Open Source Pública)
- **Estado**: Probado

## 📊 Requisitos Mínimos

| Plataforma | Configuración | Espacio |
|------------|---------------|---------|
| **Mac** | Chip M1, 16GB RAM | 20GB SSD |
| **Windows** | 16GB RAM, 6GB VRAM (NVIDIA RTX) | - |

## 📊 Hardware Recomendado (Referencias)

| Config | RAM | VRAM | Modelo Máximo |
|--------|-----|------|---------------|
| Mac M2 | 16GB | - | qwen2.5:7b |
| Mac M4 | 16GB | - | llama3.1:8b |
| RTX A2000 | 128GB | 12GB | deepseek-r1:32b |
