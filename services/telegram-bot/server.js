const TelegramBot = require('node-telegram-bot-api');
const fetch = require('node-fetch');

// =============================================
// CONFIGURACIÓN
// =============================================
const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || 'YOUR_BOT_TOKEN';
const PLANIA_API = process.env.PLANIA_API || 'http://host.docker.internal:3001';
const IA_GATEWAY = process.env.IA_GATEWAY || 'http://host.docker.internal:3002';

// Roles y permisos
const ROLES = {
    EMPRENDEDOR: 'emprendedor',  // Solo lectura
    ASESOR: 'asesor',            // Lectura + edición
    MASTER: 'master'             // Todo
};

// Base de datos de usuarios (en producción usar DB)
const users = new Map();
const sessions = new Map();

// =============================================
// INICIALIZACIÓN DEL BOT
// =============================================
const bot = new TelegramBot(BOT_TOKEN, { polling: true });

console.log('🤖 Bob (Telegram) iniciado...');
console.log('📡 Conectado a PlanIA API:', PLANIA_API);
console.log('🧠 Conectado a IA Gateway:', IA_GATEWAY);

// =============================================
// COMANDOS PRINCIPALES
// =============================================

// /start - Bienvenida e identificación
bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, `
🟡 *¡Hola! Soy Bob* 🟡
Tu asistente de PlanIA

Por favor, identifícate:

📋 */proyecto ABC123* - Ver proyecto (Emprendedor)
👔 */asesor ID123* - Acceso de asesor
🔑 */master PIN* - Acceso total

Escribe el comando según tu rol.
    `, { parse_mode: 'Markdown' });
});

// /proyecto [ID] - Emprendedor (solo lectura)
bot.onText(/\/proyecto (.+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const projectId = match[1].trim();

    // Registrar sesión como emprendedor
    sessions.set(chatId, { role: ROLES.EMPRENDEDOR, projectId });

    try {
        const response = await fetch(`${PLANIA_API}/api/projects/${projectId}`);
        if (!response.ok) {
            bot.sendMessage(chatId, '❌ Proyecto no encontrado. Verifica el ID.');
            return;
        }

        const project = await response.json();

        bot.sendMessage(chatId, `
📊 *Proyecto: ${project.nombre_negocio || 'Sin nombre'}*

👤 Emprendedor: ${project.nombre_emprendedor || 'N/A'}
📝 Descripción: ${(project.descripcion_negocio || 'Sin descripción').substring(0, 100)}...

📈 *Estado de Módulos:*
${getModuleStatus(project)}

─────────────────
📖 Solo lectura (rol: Emprendedor)
Usa /modulos para ver detalle
        `, { parse_mode: 'Markdown' });

    } catch (error) {
        bot.sendMessage(chatId, '⚠️ Error conectando con PlanIA: ' + error.message);
    }
});

// /asesor [ID] - Acceso de asesor
bot.onText(/\/asesor (.+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const asesorId = match[1].trim();

    // Validar ID de asesor (en producción verificar en DB)
    if (asesorId.length < 3) {
        bot.sendMessage(chatId, '❌ ID de asesor inválido');
        return;
    }

    sessions.set(chatId, { role: ROLES.ASESOR, asesorId });

    bot.sendMessage(chatId, `
✅ *Sesión de Asesor Iniciada*

👔 ID: ${asesorId}
🔓 Permisos: Lectura + Edición

*Comandos disponibles:*
/proyectos - Listar proyectos asignados
/ver [ID] - Ver proyecto
/editar [ID] [campo] [valor] - Modificar campo
/comentar [ID] [texto] - Agregar nota

─────────────────
⏱️ Sesión válida por 1 hora
    `, { parse_mode: 'Markdown' });
});

// /master [PIN] - Acceso total
bot.onText(/\/master (.+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const pin = match[1].trim();

    // Verificar PIN (en producción usar hash)
    const MASTER_PIN = process.env.MASTER_PIN || '1234';

    if (pin !== MASTER_PIN) {
        bot.sendMessage(chatId, '🔒 PIN incorrecto');
        return;
    }

    sessions.set(chatId, { role: ROLES.MASTER });

    bot.sendMessage(chatId, `
🔑 *Acceso MASTER Activado*

Todos los permisos habilitados:
✅ Ver todos los proyectos
✅ Editar cualquier campo
✅ Crear nuevos proyectos
✅ Ejecutar OSINT
✅ Administrar usuarios

*Comandos adicionales:*
/crear - Nuevo proyecto
/osint @usuario - Investigar usuario
/exportar [ID] - Generar PDF
/usuarios - Listar proyectos

─────────────────
⚠️ Sesión privilegiada - Cuidado con modificaciones
    `, { parse_mode: 'Markdown' });
});

// /modulos - Ver módulos del proyecto actual
bot.onText(/\/modulos/, async (msg) => {
    const chatId = msg.chat.id;
    const session = sessions.get(chatId);

    if (!session || !session.projectId) {
        bot.sendMessage(chatId, '⚠️ Primero selecciona un proyecto con /proyecto [ID]');
        return;
    }

    try {
        const response = await fetch(`${PLANIA_API}/api/projects/${session.projectId}`);
        const project = await response.json();

        const modules = [
            { name: 'Datos Generales', fields: ['nombre_negocio', 'nombre_emprendedor'] },
            { name: 'Definición', fields: ['descripcion_negocio', 'problema_oportunidad'] },
            { name: 'Mercado', fields: ['cliente_objetivo', 'segmento_cliente'] },
            { name: 'Estrategia', fields: ['propuesta_valor', 'ventaja_competitiva'] },
            { name: 'Finanzas', fields: ['monto_solicitado', 'uso_capital'] }
        ];

        let status = '📚 *Módulos del Proyecto*\n\n';
        modules.forEach((mod, i) => {
            const complete = mod.fields.every(f => project[f]);
            status += `${complete ? '✅' : '⬜'} ${i + 1}. ${mod.name}\n`;
        });

        bot.sendMessage(chatId, status, { parse_mode: 'Markdown' });

    } catch (error) {
        bot.sendMessage(chatId, '❌ Error: ' + error.message);
    }
});

// /osint @usuario - Investigación OSINT (solo Master)
bot.onText(/\/osint (.+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const session = sessions.get(chatId);

    if (!session || session.role !== ROLES.MASTER) {
        bot.sendMessage(chatId, '🔒 Comando solo disponible para rol MASTER');
        return;
    }

    const username = match[1].replace('@', '').trim();
    bot.sendMessage(chatId, `🔍 Investigando @${username}...`);

    try {
        const response = await fetch(`${IA_GATEWAY}/api/osint/user`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, timeout: 30 })
        });

        const data = await response.json();

        if (data.found > 0) {
            let result = `📊 *Resultados OSINT para @${username}*\n\n`;
            result += `Encontrados: ${data.found} perfiles\n\n`;

            data.results.slice(0, 10).forEach(r => {
                result += `• ${r.platform}: ${r.url}\n`;
            });

            bot.sendMessage(chatId, result, { parse_mode: 'Markdown' });
        } else {
            bot.sendMessage(chatId, `✅ No se encontraron perfiles para @${username}`);
        }

    } catch (error) {
        bot.sendMessage(chatId, '❌ Error en OSINT: ' + error.message);
    }
});

// /editar [ID] [campo] [valor] - Editar campo (Asesor/Master)
bot.onText(/\/editar (\S+) (\S+) (.+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const session = sessions.get(chatId);

    if (!session || session.role === ROLES.EMPRENDEDOR) {
        bot.sendMessage(chatId, '🔒 No tienes permisos para editar');
        return;
    }

    const projectId = match[1];
    const field = match[2];
    const value = match[3];

    try {
        const response = await fetch(`${PLANIA_API}/api/projects/${projectId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ [field]: value })
        });

        if (response.ok) {
            bot.sendMessage(chatId, `✅ Campo *${field}* actualizado en proyecto ${projectId}`,
                { parse_mode: 'Markdown' });
        } else {
            bot.sendMessage(chatId, '❌ Error al actualizar');
        }

    } catch (error) {
        bot.sendMessage(chatId, '❌ Error: ' + error.message);
    }
});

// /pregunta [texto] - Preguntar a Bob (IA)
bot.onText(/\/pregunta (.+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const question = match[1];

    bot.sendMessage(chatId, '🤔 Pensando...');

    try {
        const response = await fetch(`${IA_GATEWAY}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: `Eres Bob, asistente de PlanIA. Responde brevemente: ${question}`,
                stream: false
            })
        });

        const data = await response.json();
        const answer = data.response || 'No pude procesar tu pregunta.';

        bot.sendMessage(chatId, `🟡 *Bob dice:*\n\n${answer}`, { parse_mode: 'Markdown' });

    } catch (error) {
        bot.sendMessage(chatId, '❌ Error conectando con IA: ' + error.message);
    }
});

// /ayuda - Mostrar comandos
bot.onText(/\/ayuda|\/help/, (msg) => {
    const chatId = msg.chat.id;
    const session = sessions.get(chatId);
    const role = session?.role || 'ninguno';

    let help = `
🟡 *Bob - Comandos* 🟡

*Generales:*
/start - Iniciar sesión
/ayuda - Ver esta ayuda
/pregunta [texto] - Preguntar a la IA

*Emprendedor:*
/proyecto [ID] - Ver mi proyecto
/modulos - Estado de módulos
/estado - Resumen rápido
`;

    if (role === ROLES.ASESOR || role === ROLES.MASTER) {
        help += `
*Asesor:*
/proyectos - Listar asignados
/ver [ID] - Ver proyecto
/editar [ID] [campo] [valor] - Modificar
/comentar [ID] [nota] - Agregar nota
`;
    }

    if (role === ROLES.MASTER) {
        help += `
*Master:*
/crear - Nuevo proyecto
/osint @usuario - Investigar
/exportar [ID] - Generar PDF
/usuarios - Listar todos
`;
    }

    help += `\n─────────────────\nTu rol actual: *${role}*`;

    bot.sendMessage(chatId, help, { parse_mode: 'Markdown' });
});

// =============================================
// UTILIDADES
// =============================================
function getModuleStatus(project) {
    const modules = [
        { name: 'Datos Generales', check: project.nombre_negocio },
        { name: 'Definición', check: project.descripcion_negocio },
        { name: 'Mercado', check: project.cliente_objetivo },
        { name: 'Estrategia', check: project.propuesta_valor },
        { name: 'Finanzas', check: project.monto_solicitado }
    ];

    return modules.map(m => `${m.check ? '✅' : '⬜'} ${m.name}`).join('\n');
}

// Limpiar sesiones antiguas cada hora
setInterval(() => {
    const now = Date.now();
    sessions.forEach((session, chatId) => {
        if (session.timestamp && now - session.timestamp > 3600000) {
            sessions.delete(chatId);
        }
    });
}, 3600000);

console.log('✅ Bot listo para recibir mensajes');
