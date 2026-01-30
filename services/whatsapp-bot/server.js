const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fetch = require('node-fetch');

// =============================================
// CONFIGURACIÓN
// =============================================
const PLANIA_API = process.env.PLANIA_API || 'http://host.docker.internal:3001';
const IA_GATEWAY = process.env.IA_GATEWAY || 'http://host.docker.internal:3002';

// Roles y permisos
const ROLES = {
    EMPRENDEDOR: 'emprendedor',
    ASESOR: 'asesor',
    MASTER: 'master'
};

// Sesiones activas
const sessions = new Map();

// =============================================
// INICIALIZACIÓN DE WHATSAPP
// =============================================
console.log('🟢 Iniciando Bob (WhatsApp)...');

const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: '/data/whatsapp-session'
    }),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu'
        ]
    }
});

// QR Code para escanear
client.on('qr', (qr) => {
    console.log('📱 Escanea este código QR con WhatsApp:');
    qrcode.generate(qr, { small: true });

    // También guardar como imagen para acceso remoto
    const QRCode = require('qrcode');
    QRCode.toFile('/data/whatsapp-qr.png', qr, {
        width: 300,
        margin: 2
    }, (err) => {
        if (err) console.error('Error guardando QR:', err);
        else console.log('📁 QR guardado en /data/whatsapp-qr.png');
    });
});

client.on('ready', () => {
    console.log('✅ Bob (WhatsApp) conectado y listo!');
});

client.on('authenticated', () => {
    console.log('🔐 Sesión autenticada');
});

client.on('auth_failure', (msg) => {
    console.error('❌ Error de autenticación:', msg);
});

// =============================================
// MANEJO DE MENSAJES
// =============================================
client.on('message', async (msg) => {
    const text = msg.body.toLowerCase().trim();
    const sender = msg.from;

    // Ignorar grupos por ahora
    if (msg.from.includes('@g.us')) return;

    console.log(`📩 Mensaje de ${sender}: ${text}`);

    try {
        // Comandos principales
        if (text === 'hola' || text === 'inicio' || text === 'start') {
            await handleStart(msg);
        }
        else if (text.startsWith('proyecto ')) {
            await handleProject(msg, text.replace('proyecto ', '').trim());
        }
        else if (text.startsWith('asesor ')) {
            await handleAsesor(msg, text.replace('asesor ', '').trim());
        }
        else if (text.startsWith('master ')) {
            await handleMaster(msg, text.replace('master ', '').trim());
        }
        else if (text === 'modulos' || text === 'módulos') {
            await handleModulos(msg);
        }
        else if (text.startsWith('osint ')) {
            await handleOsint(msg, text.replace('osint ', '').trim());
        }
        else if (text.startsWith('editar ')) {
            await handleEdit(msg, text.replace('editar ', '').trim());
        }
        else if (text.startsWith('pregunta ') || text.startsWith('bob ')) {
            const question = text.replace(/^(pregunta|bob)\s+/i, '');
            await handleQuestion(msg, question);
        }
        else if (text === 'ayuda' || text === 'help') {
            await handleHelp(msg);
        }
        else {
            // Respuesta por defecto - preguntar a Bob
            await handleQuestion(msg, text);
        }

    } catch (error) {
        console.error('Error procesando mensaje:', error);
        await msg.reply('⚠️ Error procesando tu mensaje. Intenta de nuevo.');
    }
});

// =============================================
// HANDLERS DE COMANDOS
// =============================================

async function handleStart(msg) {
    await msg.reply(`🟡 *¡Hola! Soy Bob* 🟡
Tu asistente de PlanIA

Por favor, identifícate:

📋 *proyecto ABC123* - Ver tu proyecto
👔 *asesor ID123* - Acceso de asesor
🔑 *master PIN* - Acceso total

También puedes escribirme cualquier pregunta y trataré de ayudarte.`);
}

async function handleProject(msg, projectId) {
    const sender = msg.from;
    sessions.set(sender, { role: ROLES.EMPRENDEDOR, projectId });

    try {
        const response = await fetch(`${PLANIA_API}/api/projects/${projectId}`);
        if (!response.ok) {
            await msg.reply('❌ Proyecto no encontrado. Verifica el ID.');
            return;
        }

        const project = await response.json();

        await msg.reply(`📊 *Proyecto: ${project.nombre_negocio || 'Sin nombre'}*

👤 Emprendedor: ${project.nombre_emprendedor || 'N/A'}
📝 Descripción: ${(project.descripcion_negocio || 'Sin descripción').substring(0, 100)}...

📈 *Estado de Módulos:*
${getModuleStatus(project)}

─────────────────
📖 Solo lectura (rol: Emprendedor)
Escribe *modulos* para ver detalle`);

    } catch (error) {
        await msg.reply('⚠️ Error conectando con PlanIA');
    }
}

async function handleAsesor(msg, asesorId) {
    const sender = msg.from;

    if (asesorId.length < 3) {
        await msg.reply('❌ ID de asesor inválido');
        return;
    }

    sessions.set(sender, { role: ROLES.ASESOR, asesorId });

    await msg.reply(`✅ *Sesión de Asesor Iniciada*

👔 ID: ${asesorId}
🔓 Permisos: Lectura + Edición

*Comandos disponibles:*
• proyecto [ID] - Ver proyecto
• editar [ID] [campo] [valor] - Modificar
• modulos - Ver estado

─────────────────
⏱️ Sesión válida por 1 hora`);
}

async function handleMaster(msg, pin) {
    const sender = msg.from;
    const MASTER_PIN = process.env.MASTER_PIN || '1234';

    if (pin !== MASTER_PIN) {
        await msg.reply('🔒 PIN incorrecto');
        return;
    }

    sessions.set(sender, { role: ROLES.MASTER });

    await msg.reply(`🔑 *Acceso MASTER Activado*

Todos los permisos habilitados:
✅ Ver todos los proyectos
✅ Editar cualquier campo
✅ Ejecutar OSINT
✅ Preguntar a Bob IA

*Comandos adicionales:*
• osint @usuario - Investigar
• pregunta [texto] - Consultar IA

─────────────────
⚠️ Sesión privilegiada`);
}

async function handleModulos(msg) {
    const sender = msg.from;
    const session = sessions.get(sender);

    if (!session || !session.projectId) {
        await msg.reply('⚠️ Primero selecciona un proyecto con: proyecto [ID]');
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

        await msg.reply(status);

    } catch (error) {
        await msg.reply('❌ Error: ' + error.message);
    }
}

async function handleOsint(msg, username) {
    const sender = msg.from;
    const session = sessions.get(sender);

    if (!session || session.role !== ROLES.MASTER) {
        await msg.reply('🔒 Comando solo para rol MASTER');
        return;
    }

    username = username.replace('@', '').trim();
    await msg.reply(`🔍 Investigando @${username}...`);

    try {
        const response = await fetch(`${IA_GATEWAY}/api/osint/user`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, timeout: 30 })
        });

        const data = await response.json();

        if (data.found > 0) {
            let result = `📊 *Resultados OSINT para @${username}*\n\nEncontrados: ${data.found} perfiles\n\n`;
            data.results.slice(0, 8).forEach(r => {
                result += `• ${r.platform}: ${r.url}\n`;
            });
            await msg.reply(result);
        } else {
            await msg.reply(`✅ No se encontraron perfiles para @${username}`);
        }

    } catch (error) {
        await msg.reply('❌ Error en OSINT: ' + error.message);
    }
}

async function handleEdit(msg, params) {
    const sender = msg.from;
    const session = sessions.get(sender);

    if (!session || session.role === ROLES.EMPRENDEDOR) {
        await msg.reply('🔒 No tienes permisos para editar');
        return;
    }

    const parts = params.split(' ');
    if (parts.length < 3) {
        await msg.reply('⚠️ Formato: editar [ID] [campo] [valor]');
        return;
    }

    const projectId = parts[0];
    const field = parts[1];
    const value = parts.slice(2).join(' ');

    try {
        const response = await fetch(`${PLANIA_API}/api/projects/${projectId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ [field]: value })
        });

        if (response.ok) {
            await msg.reply(`✅ Campo *${field}* actualizado en proyecto ${projectId}`);
        } else {
            await msg.reply('❌ Error al actualizar');
        }

    } catch (error) {
        await msg.reply('❌ Error: ' + error.message);
    }
}

async function handleQuestion(msg, question) {
    await msg.reply('🤔 Pensando...');

    try {
        const response = await fetch(`${IA_GATEWAY}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: `Eres Bob, asistente de PlanIA. Responde brevemente en español: ${question}`,
                stream: false
            })
        });

        const data = await response.json();
        const answer = data.response || 'No pude procesar tu pregunta.';

        await msg.reply(`🟡 *Bob dice:*\n\n${answer.substring(0, 1500)}`);

    } catch (error) {
        await msg.reply('❌ Error conectando con IA');
    }
}

async function handleHelp(msg) {
    const sender = msg.from;
    const session = sessions.get(sender);
    const role = session?.role || 'ninguno';

    let help = `🟡 *Bob - Comandos* 🟡

*Generales:*
• hola - Iniciar
• ayuda - Ver comandos
• pregunta [texto] - Preguntar IA

*Emprendedor:*
• proyecto [ID] - Ver mi proyecto
• modulos - Estado de módulos`;

    if (role === ROLES.ASESOR || role === ROLES.MASTER) {
        help += `

*Asesor:*
• editar [ID] [campo] [valor] - Modificar`;
    }

    if (role === ROLES.MASTER) {
        help += `

*Master:*
• osint @usuario - Investigar`;
    }

    help += `\n\n─────────────────\nTu rol actual: *${role}*`;

    await msg.reply(help);
}

// =============================================
// UTILIDADES
// =============================================
function getModuleStatus(project) {
    const modules = [
        { name: 'Datos', check: project.nombre_negocio },
        { name: 'Definición', check: project.descripcion_negocio },
        { name: 'Mercado', check: project.cliente_objetivo },
        { name: 'Estrategia', check: project.propuesta_valor },
        { name: 'Finanzas', check: project.monto_solicitado }
    ];

    return modules.map(m => `${m.check ? '✅' : '⬜'} ${m.name}`).join('\n');
}

// Limpiar sesiones antiguas
setInterval(() => {
    const now = Date.now();
    sessions.forEach((session, sender) => {
        if (session.timestamp && now - session.timestamp > 3600000) {
            sessions.delete(sender);
        }
    });
}, 3600000);

// =============================================
// INICIAR CLIENTE
// =============================================
client.initialize();
