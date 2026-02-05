const termWindow = document.getElementById('chat-window');
const input = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// Config
const API_URL = 'http://localhost:3002/api/generate'; // Gateway
const SEARCH_URL = '/search'; // Local Moltbot Server

// Helper: Add Message
function addLog(text, type = 'system') {
    const div = document.createElement('div');
    div.className = `message ${type}`;

    // Markdown-ish basic parsing
    let html = text.replace(/\n/g, '<br>');
    if (type === 'assistant') {
        html = html.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
    }

    div.innerHTML = `<span class="prefix">[${type.toUpperCase()}]</span> ${html}`;
    termWindow.appendChild(div);
    termWindow.scrollTop = termWindow.scrollHeight;
}

async function handleCommand() {
    const text = input.value.trim();
    if (!text) return;

    addLog(text, 'user');
    input.value = '';

    // Check for "special" commands commands
    if (text.startsWith('/search ')) {
        const query = text.replace('/search ', '');
        await performSearch(query);
        return;
    }
    if (text.startsWith('/research ')) {
        const topic = text.replace('/research ', '');
        await performDeepResearch(topic);
        return;
    }
    if (text.startsWith('/report ')) {
        // Simple usage: /report [Topic] (Assumes we have research in history? No, let's keep it simple: Generates report from last answer)
        // ideally we pass content. For this demo, let's say /report creates a dummy report or we have to feed it content.
        // Let's make it so /research AUTOMATICALLY creating a report option.
        addLog("Usage: /research [topic] triggers both research and reporting.", 'system');
        return;
    }
    if (text.startsWith('/video ')) {
        const script = text.replace('/video ', '');
        await performVideoGen(script);
        return;
    }

    // Default: Chat with Agent
    addLog('Processing...', 'system');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: `Eres Moltbot, un agente de ciberseguridad y asistente ejecutivo.
                Responde de manera técnica, concisa y estilo "hacker".
                Usuario: ${text}`,
                stream: false,
                source: 'moltbot-terminal'
            })
        });

        const data = await response.json();
        const reply = data.response || data.choices?.[0]?.text || "No response.";

        // Remove "Processing..." last child if we tracked it, but adding new msg is fine
        addLog(reply, 'assistant');

    } catch (e) {
        addLog('Connection Error: ' + e.message, 'error');
    }
}

async function performDeepResearch(topic) {
    addLog(`🚀 Launching Deep Research Agent for: "${topic}"...`, 'system');
    addLog(`(This process involves recursive scraping and AI synthesis. Please wait...)`, 'system');

    try {
        const res = await fetch('/agent/research', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic })
        });
        const data = await res.json();

        if (data.success) {
            addLog(data.result, 'assistant');

            // Auto-generate PDF
            addLog("📄 Generating PDF Report...", 'system');
            const pdfRes = await fetch('/agent/report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: data.result, filename: `research_${Date.now()}.pdf` })
            });
            const pdfData = await pdfRes.json();
            if (pdfData.success) {
                addLog(`✅ REPORT READY: <a href="${pdfData.url}" target="_blank" style="color:#00ff41;text-decoration:underline">DOWNLOAD PDF</a>`, 'system');
            }
        } else {
            addLog('Research Failed: ' + data.error, 'error');
        }
    } catch (e) {
        addLog('Research Error: ' + e.message, 'error');
    }
}

async function performVideoGen(script) {
    addLog(`🎬 Initializing Video Studio...`, 'system');
    addLog(`Rendering video from script: "${script}"`, 'system');

    try {
        const res = await fetch('/agent/video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ script })
        });
        const data = await res.json();

        if (data.success) {
            addLog(`✅ VIDEO READY: <a href="${data.url}" target="_blank" style="color:#00ff41;text-decoration:underline">WATCH VIDEO</a>`, 'system');
        } else {
            addLog('Video Gen Failed: ' + data.error, 'error');
        }
    } catch (e) {
        addLog('Video Error: ' + e.message, 'error');
    }
}

async function performSearch(query) {
    addLog(`Initiating OSINT Search: ${query}...`, 'system');
    try {
        const res = await fetch(SEARCH_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const data = await res.json();

        if (data.results) {
            let summary = `Search Results (${data.count}):<br>`;
            data.results.forEach(r => {
                summary += `<br>🔗 <a href="${r.url}" target="_blank" style="color:#fff">${r.title}</a><br><i>${r.snippet}</i><br>`;
            });
            addLog(summary, 'assistant');
        } else {
            addLog('No results found.', 'system');
        }

    } catch (e) {
        addLog('Search Failed: ' + e.message, 'error');
    }
}

// Events
sendBtn.addEventListener('click', handleCommand);
input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleCommand();
});

// Check Gateway Status
fetch(API_URL.replace('/api/generate', '/health'))
    .then(r => {
        if (r.ok) document.querySelector('.sys-info .warning').textContent = "CONNECTED";
        else document.querySelector('.sys-info .warning').textContent = "ERROR";
        document.querySelector('.sys-info .warning').className = "success";
    })
    .catch(() => {
        document.querySelector('.sys-info .warning').textContent = "DISCONNECTED";
        document.querySelector('.sys-info .warning').className = "danger";
    });
