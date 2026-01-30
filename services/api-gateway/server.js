/**
 * IA TOOLS - API Gateway Centralizado v3
 * =======================================
 * Hub central con detección de plataforma:
 * - MacOS → MLX (Gemma3 4b Multimodal)
 * - Windows → Ollama (Gemma3 1b)
 * - Moltbot/OSINT (Sherlock, WHOIS)
 * - Whisper (Transcripción)
 */

const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const os = require('os');

const app = express();
const PORT = process.env.PORT || 3002;

// ============================================
// DETECCIÓN DE PLATAFORMA (desde env o auto)
// ============================================
const PLATFORM = process.env.HOST_PLATFORM || os.platform(); // 'darwin' (Mac), 'win32' (Windows)
const IS_MAC = PLATFORM === 'darwin';
const IS_WINDOWS = PLATFORM === 'win32' || PLATFORM === 'windows';

// Config de backends
const MLX_HOST = process.env.MLX_HOST || 'http://localhost:8000';
const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://localhost:11434';
const MOLTBOT_CONTAINER = 'ai-moltbot';
const WHISPER_HOST = process.env.WHISPER_HOST || 'http://ai-whisper:9000';

// Backend activo según plataforma
const AI_BACKEND = IS_MAC ? 'mlx' : 'ollama';
const AI_HOST = IS_MAC ? MLX_HOST : OLLAMA_HOST;
const DEFAULT_MODEL = IS_MAC ? 'gemma-3-4b-it' : 'gemma3:1b';

console.log(`🖥️  Platform: ${PLATFORM}`);
console.log(`🤖 AI Backend: ${AI_BACKEND} (${AI_HOST})`);
console.log(`📦 Default Model: ${DEFAULT_MODEL}`);

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.static(path.join(__dirname, 'public')));

const upload = multer({ dest: '/tmp/uploads/' });

// ============================================
// LOGGING SYSTEM (MySQL)
// ============================================
const LOG_API_URL = 'http://host.docker.internal:8080/api/log_ai.php';

async function logToDB(data) {
    try {
        // Fire and forget (don't await)
        fetch(LOG_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).catch(err => console.error('Logging Error:', err.message));
    } catch (e) {
        console.error('Logging Failed:', e);
    }
}

// ============================================
// HEALTH CHECK
// ============================================
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        service: 'ia-tools-gateway',
        version: '3.0.0',
        platform: PLATFORM,
        backend: AI_BACKEND,
        model: DEFAULT_MODEL,
        services: {
            ai: AI_HOST,
            moltbot: MOLTBOT_CONTAINER,
            whisper: WHISPER_HOST
        }
    });
});

// ============================================
// AI GENERATE (Unified)
// ============================================
app.post('/api/generate', async (req, res) => {
    try {
        const { prompt, model, stream = false, options, user_id, source } = req.body;
        const useModel = model || DEFAULT_MODEL;

        if (AI_BACKEND === 'mlx') {
            // MLX usa formato OpenAI
            const response = await fetch(`${MLX_HOST}/v1/completions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: useModel,
                    prompt: prompt,
                    max_tokens: options?.num_predict || 1024,
                    temperature: options?.temperature || 0.7
                })
            });
            const data = await response.json();
            const output = data.choices?.[0]?.text || '';

            // Convertir formato OpenAI a formato Ollama
            res.json({
                response: output,
                model: useModel,
                backend: 'mlx'
            });
            // Log Async
            logToDB({
                source: source || 'unknown',
                user_id: user_id || 'anonymous',
                prompt: prompt,
                response: output,
                model: useModel,
                metadata: { backend: 'mlx', options }
            });
        } else {
            // Ollama
            const response = await fetch(`${OLLAMA_HOST}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: useModel, prompt, stream, options })
            });
            const data = await response.json();
            data.backend = 'ollama';
            res.json(data);
        }
    } catch (error) {
        // Fallback a Ollama si MLX falla
        if (AI_BACKEND === 'mlx') {
            console.log('⚠️ MLX failed, falling back to Ollama');
            try {
                const { prompt, model, stream = false, options, user_id, source } = req.body;
                const response = await fetch(`${OLLAMA_HOST}/api/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ model: 'gemma3:1b', prompt, stream, options })
                });
                const data = await response.json();
                data.backend = 'ollama-fallback';

                // Send response
                res.json(data);

                // Log safe
                try {
                    logToDB({
                        source: source || 'unknown',
                        user_id: user_id || 'anonymous',
                        prompt: prompt,
                        response: data.response,
                        model: 'gemma3:1b',
                        metadata: { backend: 'ollama-fallback', options }
                    });
                } catch (errLog) { console.error('Log error', errLog); }
                return;
            } catch (e) {
                // Only send error if headers not sent
                if (!res.headersSent) {
                    return res.status(500).json({ error: e.message });
                }
            }
        }
        if (!res.headersSent) res.status(500).json({ error: error.message });
    }
});

// ============================================
// AI CHAT (Unified)
// ============================================
app.post('/api/chat', async (req, res) => {
    try {
        const { messages, model, stream = false, user_id, source } = req.body;
        const useModel = model || DEFAULT_MODEL;

        // Extract last user message for logging
        const lastMsg = messages[messages.length - 1]?.content || '';

        if (AI_BACKEND === 'mlx') {
            // MLX usa formato OpenAI chat
            const response = await fetch(`${MLX_HOST}/v1/chat/completions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: useModel,
                    messages: messages,
                    max_tokens: 1024,
                    temperature: 0.7
                })
            });
            const data = await response.json();

            res.json({
                message: { content: data.choices?.[0]?.message?.content || '' },
                model: useModel,
                backend: 'mlx'
            });

            logToDB({
                source: source || 'unknown',
                user_id: user_id || 'anonymous',
                prompt: lastMsg,
                response: data.choices?.[0]?.message?.content || '',
                model: useModel,
                metadata: { backend: 'mlx', full_history: messages }
            });
        } else {
            const response = await fetch(`${OLLAMA_HOST}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: useModel, messages, stream })
            });
            const data = await response.json();
            data.backend = 'ollama';
            res.json(data);
        }
    } catch (error) {
        // Fallback to Ollama if MLX fails
        if (AI_BACKEND === 'mlx') {
            console.log('⚠️ MLX Chat failed, falling back to Ollama');
            try {
                const { messages, model, stream = false, source, user_id } = req.body;
                // Force fallback model
                const fallbackModel = 'gemma3:1b';

                const response = await fetch(`${OLLAMA_HOST}/api/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ model: fallbackModel, messages, stream })
                });
                const data = await response.json();
                data.backend = 'ollama-fallback';
                res.json(data);

                // Log Fallback
                /*
                logToDB({
                    source: source || 'unknown',
                    user_id: user_id || 'anonymous',
                    prompt: messages[messages.length - 1]?.content || '',
                    response: data.message?.content || '',
                    model: fallbackModel,
                    metadata: { backend: 'ollama-fallback' }
                });
                */
                return;
            } catch (e) {
                return res.status(500).json({ error: 'Fallback failed: ' + e.message });
            }
        }
        res.status(500).json({ error: error.message });
    }
});

// ============================================
// OSINT - Sherlock (User Search)
// ============================================
// ============================================
// OSINT - Sherlock (User Search)
// ============================================
app.post('/api/osint/user', async (req, res) => {
    try {
        // Proxy to local Moltbot service (Native)
        const response = await fetch(`http://localhost:3005/osint/user`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(req.body)
        });
        const data = await response.json();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: 'Moltbot OSINT error: ' + error.message });
    }
});

// ============================================
// OSINT - Domain Info (WHOIS)
// ============================================
app.post('/api/osint/domain', async (req, res) => {
    // Implement or Proxy
});

// ============================================
// MOLTBOT - Headless Scraping
// ============================================
app.post('/api/scrape', async (req, res) => {
    try {
        // Proxy to local Moltbot service (Native)
        const response = await fetch(`http://localhost:3005/scrape`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(req.body)
        });
        const data = await response.json();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: 'Moltbot Scrape error: ' + error.message });
    }
});

// ============================================
// WHISPER - Transcription
// ============================================
app.post('/api/transcribe', upload.single('audio'), async (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'audio file is required' });
    }

    try {
        const FormData = require('form-data');
        const form = new FormData();
        form.append('audio_file', fs.createReadStream(req.file.path));

        const response = await fetch(`${WHISPER_HOST}/asr?output=json`, {
            method: 'POST',
            body: form
        });

        const data = await response.json();
        fs.unlinkSync(req.file.path);
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ============================================
// MODELS - List/Pull
// ============================================
app.get('/api/models', async (req, res) => {
    try {
        const response = await fetch(`${OLLAMA_HOST}/api/tags`);
        const data = await response.json();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ============================================
// ROUTES
// ============================================
app.get('/osint', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'osint.html'));
});

// Dashboard
app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html>
<head>
    <title>IA Tools Gateway v3</title>
    <style>
        body { font-family: system-ui; background: #1a1a2e; color: #eee; padding: 40px; }
        h1 { color: #00d9ff; }
        .card { background: #16213e; padding: 20px; margin: 15px 0; border-radius: 12px; }
        .method { color: #4ade80; font-weight: bold; }
        code { background: #0f3460; padding: 3px 10px; border-radius: 6px; }
        .status { color: #4ade80; font-size: 1.2em; }
        a { color: #00d9ff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .badge { background: #a855f7; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; }
    </style>
</head>
<body>
    <h1>🤖 IA Tools Gateway v3</h1>
    <p class="status">✅ Running on port ${PORT}</p>
    <p>Platform: <span class="badge">${PLATFORM}</span> | Backend: <span class="badge">${AI_BACKEND}</span> | Model: <span class="badge">${DEFAULT_MODEL}</span></p>
    
    <h2>🔗 Quick Links</h2>
    <div class="card">
        <a href="/osint">🔍 OSINT Tools (User & Domain Search)</a>
    </div>
    
    <h2>📡 API Endpoints</h2>
    <div class="card">
        <span class="method">POST</span> <code>/api/generate</code> - Generate text (${AI_BACKEND})
    </div>
    <div class="card">
        <span class="method">POST</span> <code>/api/chat</code> - Chat conversation (${AI_BACKEND})
    </div>
    <div class="card">
        <span class="method">POST</span> <code>/api/osint/user</code> - Search user (Sherlock)
    </div>
    <div class="card">
        <span class="method">POST</span> <code>/api/osint/domain</code> - Domain info (WHOIS)
    </div>
    <div class="card">
        <span class="method">POST</span> <code>/api/transcribe</code> - Audio to text (Whisper)
    </div>
</body>
</html>
    `);
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`\n🚀 IA Tools Gateway v3 running on port ${PORT}`);
    console.log(`   Dashboard: http://localhost:${PORT}`);
    console.log(`   OSINT UI: http://localhost:${PORT}/osint`);
});
