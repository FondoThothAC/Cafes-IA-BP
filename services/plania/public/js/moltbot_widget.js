/**
 * Moltbot Widget
 * Unified AI Assistant for PlanIA Modules
 */

(function () {
    // Config - Detectar host dinámicamente para soportar acceso remoto
    const ERROR_LOG = [];
    const host = window.location.hostname;
    const gatewayPort = 3002;
    const AI_CHAT_API = `http://${host}:${gatewayPort}/api/generate`;
    const SEARCH_API = `http://${host}:8085/search`;
    const OSINT_API = `http://${host}:8085/osint/user`;

    // Auto-detect path
    const JS_PATH = document.currentScript ? document.currentScript.src : 'js/moltbot_widget.js';
    const CSS_PATH = JS_PATH.replace('js/moltbot_widget.js', 'css/moltbot.css');

    // Inject CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = CSS_PATH;
    document.head.appendChild(link);

    // HTML Template
    const htmlTemplate = `
        <button id="ai-fab" onclick="window.Moltbot.toggle()" title="Asistente Moltbot">
            <div style="width: 40px; height: 40px; border-radius: 50%; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                 <img src="img/bob-logo.png" alt="MB" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjIiPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIi8+PHBhdGggZD0iTTggMTRoOG0tOC00aDgiLz48L3N2Zz4='">
            </div>
        </button>

        <div id="ai-chat-panel">
            <div class="ai-chat-header">
                <div style="width: 36px; height: 36px; border-radius: 50%; overflow: hidden;">
                    <img src="img/bob-logo.png" alt="MB" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.onerror=null;this.src='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjIiPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIi8+PHBhdGggZD0iTTggMTRoOG0tOC00aDgiLz48L3N2Zz4='">
                </div>
                <div style="flex: 1;">
                    <h3>BoB IA - Agente</h3>
                    <span class="badge">BoB (Moltbot Core)</span>
                </div>
                <button onclick="window.Moltbot.resetChat()" title="Reiniciar Chat" style="background: none; border: none; color: white; cursor: pointer; font-size: 1.2rem;">🔄</button>
            </div>

            <div class="ai-chat-messages" id="ai-chat-messages">
                <div class="ai-msg assistant">
                    <div class="ai-msg-content">
                        ¡Hola! Soy <strong>BoB IA</strong>, tu agente experto de PlanIA.
                        <br>Estoy aquí para ayudarte en este módulo.
                        <br>💡 Puedes pedirme que investigue, sugiera datos o analice la información.
                    </div>
                </div>
            </div>

            <div class="ai-quick-actions">
                <button class="ai-quick-btn" onclick="window.Moltbot.quickAction('suggest')">💡 Sugerir Datos</button>
                <button class="ai-quick-btn" onclick="window.Moltbot.quickAction('research')">🔍 Investigar Web</button>
                <button class="ai-quick-btn" onclick="window.Moltbot.quickAction('analyze')">📊 Analizar</button>
            </div>

            <div class="ai-chat-input">
                <input type="text" id="ai-chat-input" placeholder="Pregunta algo..."
                    onkeypress="if(event.key==='Enter') window.Moltbot.send()">
                <button onclick="window.Moltbot.send()">➤</button>
            </div>
        </div>
    `;

    // Inject HTML on Load
    document.addEventListener('DOMContentLoaded', () => {
        const div = document.createElement('div');
        div.id = 'moltbot-container';
        div.innerHTML = htmlTemplate;
        document.body.appendChild(div);

        // Make Draggable
        const panel = document.getElementById('ai-chat-panel');
        const header = panel.querySelector('.ai-chat-header');

        let isDragging = false;
        let startX, startY, initialLeft, initialTop;

        header.addEventListener('mousedown', (e) => {
            isDragging = true;

            // Get current computed position
            const style = window.getComputedStyle(panel);
            // If right/bottom are set, we need to switch to left/top for dragging logic or handle offsets
            // Simplest: use offsetLeft/Top logs

            // Reset right/bottom to auto if we are going to use left/top
            const rect = panel.getBoundingClientRect();
            panel.style.right = 'auto';
            panel.style.bottom = 'auto';
            panel.style.left = rect.left + 'px';
            panel.style.top = rect.top + 'px';
            panel.style.width = rect.width + 'px'; // Fix width during drag to prevent resize glitch

            startX = e.clientX;
            startY = e.clientY;
            initialLeft = rect.left;
            initialTop = rect.top;

            header.style.cursor = 'grabbing';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            panel.style.left = `${initialLeft + dx}px`;
            panel.style.top = `${initialTop + dy}px`;
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                header.style.cursor = 'move';
            }
        });
    });

    // Core Logic
    window.Moltbot = {
        toggle: function () {
            const panel = document.getElementById('ai-chat-panel');
            const fab = document.getElementById('ai-fab');
            panel.classList.toggle('open');
            fab.classList.toggle('active');

            const isOpen = panel.classList.contains('open');
            if (isOpen) {
                fab.innerHTML = '✕';
            } else {
                fab.innerHTML = '<div style="width: 40px; height: 40px; border-radius: 50%; overflow: hidden; display: flex; align-items: center; justify-content: center;"><img src="img/bob-logo.png" alt="Bob" style="width: 100%; height: 100%; object-fit: cover;"></div>';
            }
        },

        resetChat: function () {
            const messages = document.getElementById('ai-chat-messages');
            messages.innerHTML = `
                <div class="ai-msg assistant">
                    <div class="ai-msg-content">
                        ♻️ Chat reiniciado.<br>
                        ¡Hola de nuevo! Soy <strong>BoB IA</strong>. ¿En qué te ayudo ahora?
                    </div>
                </div>
            `;
        },

        addMessage: function (content, role = 'assistant') {
            const messages = document.getElementById('ai-chat-messages');
            const time = new Date().toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
            const msg = document.createElement('div');
            msg.className = `ai-msg ${role}`;
            msg.innerHTML = `
                <div class="ai-msg-content">${content}</div>
                <div class="ai-msg-time">${time}</div>
            `;
            messages.appendChild(msg);
            messages.scrollTop = messages.scrollHeight;
        },

        showTyping: function () {
            const messages = document.getElementById('ai-chat-messages');
            const typing = document.createElement('div');
            typing.id = 'ai-typing-indicator';
            typing.className = 'ai-msg assistant';
            typing.innerHTML = '<div class="ai-typing"><span></span><span></span><span></span></div>';
            messages.appendChild(typing);
            messages.scrollTop = messages.scrollHeight;
        },

        hideTyping: function () {
            const typing = document.getElementById('ai-typing-indicator');
            if (typing) typing.remove();
        },

        getFormContext: function () {
            const fields = {};
            const title = document.querySelector('h1')?.innerText || document.title;
            fields['_page_title'] = title;

            document.querySelectorAll('input, textarea, select').forEach(el => {
                const key = el.id || el.name;
                if (key && el.value && el.type !== 'hidden' && el.type !== 'submit') {
                    fields[key] = el.value;
                }
            });

            const availableFields = Array.from(document.querySelectorAll('input[id], textarea[id], select[id]'))
                .map(el => el.id)
                .filter(id => !['ai-chat-input'].includes(id));

            fields['_available_fields'] = availableFields.join(', ');
            return fields;
        },

        getUserID: function () {
            const el = document.getElementById('uuid_usuario');
            if (el && el.value) return el.value;
            if (localStorage.getItem('user_id')) return localStorage.getItem('user_id');
            return 'anonymous-' + Math.random().toString(36).substr(2, 9);
        },

        send: async function (overridePrompt = null) {
            const input = document.getElementById('ai-chat-input');
            const message = input.value.trim();
            if (!message && !overridePrompt) return;

            if (message) this.addMessage(message, 'user');
            input.value = '';
            this.showTyping();

            const context = this.getFormContext();
            const source = window.location.pathname.split('/').pop() || 'unknown-page';

            const contextStr = Object.keys(context).length > 0
                ? `\n\nContexto de la página actual (${context._page_title}):\n${JSON.stringify(context, null, 2)}`
                : '';

            // Auto-detect "Agentic" intent: research request
            const researchKeywords = ['precio', 'buscar', 'investiga', 'encontrar', '2026', 'hoy', 'dato', 'cuanto', 'cuánto'];
            if (!overridePrompt && researchKeywords.some(kw => message.toLowerCase().includes(kw))) {
                this.addMessage('🤖 Detecté una solicitud de investigación. Buscando en la web...', 'system');
                this.quickAction('research', message);
                return;
            }

            let prompt = overridePrompt || `Eres BoB IA (basado en Moltbot), agente experto de Fondo Thoth.
            Fecha actual: ${new Date().toLocaleDateString()}
            Estás ayudando al usuario en el módulo: ${context._page_title}.
            
            ${((typeof PlanIA !== 'undefined') && PlanIA.getProjectContextMD()) ?
                    'DATOS DEL PROYECTO SELECCIONADO:\n' + PlanIA.getProjectContextMD() :
                    '⚠️ NO HAY PROYECTO SELECCIONADO. Pide al usuario que seleccione un proyecto en el menú superior.'}
            
            Contexto de campos en pantalla:
            ${contextStr}

            Usuario: ${message}

            INSTRUCCIONES CRÍTICAS:
            1. RESPONDE SIEMPRE EN ESPAÑOL DE MÉXICO PROFESIONAL.
            2. NO uses inglés a menos que sea un término técnico indispensable.
            3. USA LOS DATOS DEL PROYECTO para dar respuestas específicas y contextualizadas.
            4. Si no hay proyecto seleccionado, PRIMERO pide al usuario que seleccione uno.

            Tu tarea:
            1. Responde la duda del usuario usando los datos reales del proyecto.
            2. Si detectas información que debería ir en un campo disponible (ver _available_fields), sugiérela en formato: 
               campo_id: "valor sugerido"
            3. Si mencionas un precio o dato investigado, DEBES citar la fuente en formato JSON al final:
               [SOURCE: {"title": "Titulo", "url": "URL", "context": "Precio de X"}]
            
            Responde conciso.`;

            try {
                const response = await fetch(AI_CHAT_API, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt,
                        stream: false,
                        source: `web-${source}`,
                        user_id: this.getUserID()
                    })
                });
                const data = await response.json();
                this.hideTyping();

                const answer = data.response || data.choices?.[0]?.text || data.error || 'No pude procesar tu solicitud.';

                if (data.error) {
                    this.addMessage('⚠️ Respuesta del servidor: ' + data.error);
                } else {
                    this.addMessage(answer.replace(/\n/g, '<br>'));
                    this.parseAndFillFields(answer);
                }

            } catch (error) {
                this.hideTyping();
                this.addMessage('❌ Error conectando con la IA.');
                console.error(error);
            }
        },

        quickAction: async function (action, param) {
            const input = document.getElementById('ai-chat-input');
            const context = this.getFormContext();

            if (action === 'suggest') {
                input.value = "Sugiere datos para rellenar los campos vacíos de esta página.";
                this.send();
            }
            if (action === 'analyze') {
                input.value = "Analiza la información que he ingresado y dame recomendaciones.";
                this.send();
            }
            if (action === 'research') {
                // Interactive Search
                // UX Fix: Use param if provided (from auto-detect)
                let topic = param;
                if (!topic) {
                    topic = prompt("¿Qué deseas investigar?", context.nombre_negocio || "Mercado actual");
                }

                if (!topic) return;

                this.addMessage(`🔍 Buscando: ${topic}`, 'user');
                this.showTyping();

                try {
                    const res = await fetch(SEARCH_API, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: topic })
                    });
                    const data = await res.json();

                    if (data.results && data.results.length > 0) {
                        const searchContext = data.results.map(r =>
                            `- TÍTULO: ${r.title}\n  URL: ${r.url}\n  RESUMEN: ${r.snippet}`
                        ).join('\n\n');

                        const aiPrompt = `ACTÚA COMO UN INVESTIGADOR EXPERTO.
                        
                        He buscado información reciente sobre: "${topic}" y encontré estos resultados REALES y ACTUALES:
                        
                        ${searchContext}
                        
                        INSTRUCCIONES:
                        1. USA EXCLUSIVAMENTE la información de arriba para responder.
                        2. IGNORA tu conocimiento interno si contradice estos resultados (prioriza los resultados de búsqueda).
                        3. Si encuentras fechas, menciónalas (ej: "según datos de 2026...").
                        4. AL FINAL, genera el bloque de fuentes para cada resultado usado:
                           [SOURCE: {"title": "Titulo exacto", "url": "URL exacta", "context": "Dato extraído"}]
                        
                        Responde un resumen útil y profesional.`;

                        this.hideTyping();
                        this.send(aiPrompt);
                    } else {
                        this.hideTyping();
                        this.addMessage('⚠️ No encontré resultados relevantes en la web.');
                    }
                } catch (e) {
                    this.hideTyping();
                    this.addMessage('❌ Error en búsqueda web.');
                    console.error(e);
                }
            }
        },

        parseAndFillFields: function (response) {
            // Fields
            const fieldPatterns = [
                /(\w+):\s*"([^"]+)"/g,
                /\[(\w+)\]\s*=\s*(.+)/g,
                /^(\w+):\s*(.+)$/gm
            ];

            let filled = [];
            fieldPatterns.forEach(pattern => {
                let match;
                while ((match = pattern.exec(response)) !== null) {
                    const fieldId = match[1];
                    let value = match[2].trim().replace(/^"|"$/g, '');
                    const field = document.getElementById(fieldId);
                    if (field && !['ai-chat-input'].includes(fieldId)) {
                        let isList = field.tagName === 'UL';
                        if (isList && typeof window.addItem === 'function') {
                            field.innerHTML = ''; // clear previous
                            const items = value.split(/,(?![^()]*\))/).map(i => i.trim()).filter(i => i);
                            items.forEach(i => window.addItem(fieldId, i));

                            field.style.border = "2px solid #10b981";
                            setTimeout(() => field.style.border = "", 2000);
                            filled.push(fieldId);
                        } else if (!isList) {
                            field.value = value;
                            field.dispatchEvent(new Event('input', { bubbles: true }));
                            field.style.border = "2px solid #10b981";
                            setTimeout(() => field.style.border = "", 2000);
                            filled.push(fieldId);
                        }
                    }
                }
            });
            if (filled.length > 0) this.addMessage(`✅ Actualicé: ${filled.join(', ')}`);

            // Sources
            const sourceRegex = /\[SOURCE:\s*({.+?})\]/g;
            let sMatch;
            while ((sMatch = sourceRegex.exec(response)) !== null) {
                try {
                    const sourceData = JSON.parse(sMatch[1]);
                    // Auto-Add to Sources Module via global hook
                    if (window.addAutoSource) {
                        window.addAutoSource(sourceData);
                        this.addMessage(`📚 Fuente guardada: <a href="${sourceData.url}" target="_blank">${sourceData.title}</a>`);
                    } else {
                        // Fallback if not on sources page: Try to save via API or LocalStorage?
                        // Ideally, we access the sources list from localStorage/DB.
                        console.log("Source found but addAutoSource not available:", sourceData);
                    }
                } catch (e) { console.error('Bad source JSON', e); }
            }
        }
    };

    window.MoltbotWidget = window.Moltbot;
})();
