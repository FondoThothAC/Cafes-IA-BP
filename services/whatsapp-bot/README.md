# 📱 Bob - WhatsApp Bot Setup

## ⚠️ Importante

WhatsApp **NO tiene API oficial gratuita** para bots. Usamos `whatsapp-web.js` que simula WhatsApp Web.

**Riesgos:**
- WhatsApp puede banear el número si detecta automatización excesiva
- Requiere escanear QR la primera vez
- Si usas tu número personal, ten cuidado

**Alternativa recomendada:** Usar primero el bot de Telegram que es 100% oficial.

---

## Paso 1: Iniciar el Bot

```bash
cd /Users/robertoeduardocelisrobles/Documents/FT\ Apps/AI-Toolkit

# Construir y levantar
docker-compose up -d --build whatsapp-bot
```

## Paso 2: Escanear QR

```bash
# Ver logs para QR code
docker logs -f bob-whatsapp
```

Aparecerá un código QR en la terminal. Escanéalo con WhatsApp:
1. Abre WhatsApp en tu teléfono
2. Ve a Configuración → Dispositivos vinculados
3. Escanea el código QR

El QR también se guarda en: `/data/whatsapp-qr.png`

## Paso 3: Probar

Envía un mensaje al número vinculado:

```
hola
```

Debería responder con el menú de Bob.

## Comandos

| Comando | Rol | Descripción |
|---------|-----|-------------|
| `hola` | Todos | Bienvenida |
| `ayuda` | Todos | Ver comandos |
| `proyecto [ID]` | Emprendedor | Ver proyecto |
| `modulos` | Emprendedor | Estado módulos |
| `asesor [ID]` | Asesor | Iniciar sesión asesor |
| `editar [ID] [campo] [valor]` | Asesor+ | Modificar campo |
| `master [PIN]` | Master | Acceso total |
| `osint @usuario` | Master | Investigar usuario |
| `pregunta [texto]` | Todos | Preguntar a Bob IA |

## Troubleshooting

### QR no aparece
```bash
docker-compose restart whatsapp-bot
docker logs -f bob-whatsapp
```

### Sesión expiró
```bash
# Eliminar sesión anterior
docker volume rm ai-toolkit_whatsapp_data
docker-compose up -d --build whatsapp-bot
```

### Bot no responde
Verificar que el Gateway esté corriendo:
```bash
docker ps | grep gateway
```
