# 🤖 Bob - Telegram Bot Setup

## Paso 1: Crear Bot en Telegram

1. Abre Telegram y busca **@BotFather**
2. Envía `/newbot`
3. Nombre del bot: `Bob PlanIA`
4. Username: `bob_plania_bot` (debe terminar en `_bot`)
5. **Copia el token** que te da BotFather

## Paso 2: Configurar Token

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar y pegar tu token
nano .env
```

Pegar tu token en:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

## Paso 3: Iniciar Servicios

```bash
cd /Users/robertoeduardocelisrobles/Documents/FT\ Apps/AI-Toolkit

# Construir y levantar
docker-compose up -d --build telegram-bot mysql-db
```

## Paso 4: Probar

1. Busca tu bot en Telegram: `@bob_plania_bot`
2. Envía `/start`
3. Prueba comandos:
   - `/proyecto ABC123` (Emprendedor)
   - `/asesor TU_ID` (Asesor)
   - `/master 1234` (Master)

## Comandos Disponibles

| Comando | Rol | Descripción |
|---------|-----|-------------|
| `/start` | Todos | Bienvenida |
| `/ayuda` | Todos | Ver comandos |
| `/proyecto [ID]` | Emprendedor | Ver proyecto |
| `/modulos` | Emprendedor | Estado módulos |
| `/editar [ID] [campo] [valor]` | Asesor+ | Modificar |
| `/osint @usuario` | Master | Investigar |
| `/pregunta [texto]` | Todos | Preguntar a IA |

## Troubleshooting

### Bot no responde
```bash
docker logs bob-telegram
```

### Token inválido
Verificar que el token en `.env` sea correcto (sin espacios).

### Permisos
Si usas `/osint`, asegúrate que Moltbot esté corriendo.
