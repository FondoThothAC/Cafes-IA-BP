const express = require('express');
const cors = require('cors');
const puppeteer = require('puppeteer-core');
const { exec } = require('child_process');

// Importaciones de Capacidades (Skills)
const { deepResearch } = require('./src/capabilities/researcher');
const { createPDF, createVideo } = require('./src/capabilities/producer');

const app = express();
// ==========================================
// CONFIGURACIÓN
// ==========================================
const PORT = process.env.PORT || 8080;

app.use(cors());
app.use(express.json());

// Servir UI Dedicada (Dashboard)
app.use(express.static('public'));

// Configuración de Puppeteer para Alpine Linux
// Configuración de Puppeteer (Detectar entorno: Mac vs Linux/Docker)
const os = require('os');
const isMac = os.platform() === 'darwin';

const PUPPETEER_OPTIONS = {
    executablePath: isMac
        ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        : '/usr/bin/chromium-browser',
    headless: 'new',
    args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions',
        '--lang=es-MX,es' // Force Spanish locale for results
    ]
};

// ==========================================
// ENDPOINT: Scraping Headless
// ==========================================
app.post('/scrape', async (req, res) => {
    const { url, selectors } = req.body;

    if (!url) return res.status(400).json({ error: 'URL requerida' });

    console.log(`🕷️ Scraping: ${url}`);
    let browser = null;

    try {
        browser = await puppeteer.launch(PUPPETEER_OPTIONS);
        const page = await browser.newPage();

        // Anti-bot básico
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36');

        await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

        // Extraer datos
        const title = await page.title();
        const content = await page.evaluate(() => document.body.innerText.substring(0, 5000));

        let extractedData = {};

        // Si piden selectores específicos
        if (selectors && Array.isArray(selectors)) {
            for (const sel of selectors) {
                extractedData[sel] = await page.evaluate((s) => {
                    const el = document.querySelector(s);
                    return el ? el.innerText : null;
                }, sel);
            }
        }

        res.json({
            success: true,
            title,
            length: content.length,
            content: content.replace(/\s+/g, ' ').trim(),
            data: extractedData
        });

    } catch (error) {
        console.error('Error Puppeteer:', error);
        res.status(500).json({ success: false, error: error.message });
    } finally {
        if (browser) await browser.close();
    }
});

// ==========================================
// ENDPOINT: Search (DuckDuckGo Scraper)
// ==========================================
app.post('/search', async (req, res) => {
    const { query } = req.body;
    if (!query) return res.status(400).json({ error: 'Query requerido' });

    console.log(`🔎 Buscando en web: ${query}`);
    let browser = null;

    try {
        browser = await puppeteer.launch(PUPPETEER_OPTIONS);
        const page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36');

        // DuckDuckGo Search
        await page.goto(`https://duckduckgo.com/?q=${encodeURIComponent(query)}&kl=mx-es`, { waitUntil: 'networkidle2', timeout: 30000 });

        const results = await page.evaluate(() => {
            // 1. Try to get Instant Answer (Calculator/Converter)
            const answerEl = document.querySelector('.c-base__title') || document.querySelector('#zci-result') || document.querySelector('.zci__def__text');
            const answerSub = document.querySelector('.c-base__sub') || document.querySelector('.zci__def__sub');

            let instantAnswer = null;
            if (answerEl) {
                instantAnswer = {
                    title: "Respuesta Rápida (Instant Answer)",
                    url: "https://duckduckgo.com",
                    snippet: "DATOS EXACTOS: " + answerEl.innerText + (answerSub ? " " + answerSub.innerText : "")
                };
            }

            // 2. Get Standard Results
            const items = document.querySelectorAll('article');
            const data = [];

            if (instantAnswer) data.push(instantAnswer);

            items.forEach(item => {
                const titleEl = item.querySelector('h2 a');
                const linkEl = item.querySelector('h2 a');
                const snippetEl = item.querySelector('[data-result="snippet"]');

                if (titleEl && linkEl) {
                    data.push({
                        title: titleEl.innerText,
                        url: linkEl.href,
                        snippet: snippetEl ? snippetEl.innerText : ''
                    });
                }
            });
            return data.slice(0, 6); // Return top 6
        });

        res.json({ success: true, count: results.length, results });

    } catch (error) {
        console.error('Error Search:', error);
        res.status(500).json({ success: false, error: error.message });
    } finally {
        if (browser) await browser.close();
    }
});

// ==========================================
// ENDPOINT: OSINT (Sherlock)
// ==========================================
app.post('/osint/user', async (req, res) => {
    const { username } = req.body;
    if (!username) return res.status(400).json({ error: 'Username requerido' });

    console.log(`🔍 Buscando usuario: ${username}`);

    // Ejecutar Sherlock (Python)
    const cmd = `python3 /usr/bin/sherlock ${username} --timeout 5 --print-found`;

    exec(cmd, (error, stdout, stderr) => {
        if (error) {
            console.error('Error Sherlock:', error);
            // Sherlock retorna error si no encuentra nada o si falla algo, pero a veces stdout tiene info
        }

        // Parsear salida
        const lines = stdout.split('\n');
        const results = lines
            .filter(line => line.includes('http'))
            .map(line => {
                const parts = line.split(': ');
                return { platform: parts[0]?.trim(), url: parts[1]?.trim() };
            })
            .filter(r => r.url);

        res.json({
            success: true,
            username,
            found: results.length,
            results
        });
    });
});

app.post('/agent/research', async (req, res) => {
    const { topic } = req.body;
    try {
        const report = await deepResearch(topic);
        res.json({ success: true, result: report });
    } catch (e) {
        res.status(500).json({ success: false, error: e.message });
    }
});

app.post('/agent/report', async (req, res) => {
    const { content, filename } = req.body;
    try {
        const file = await createPDF(content, filename || `report_${Date.now()}.pdf`);
        res.json({ success: true, url: `http://localhost:${PORT}/${file}` });
    } catch (e) {
        res.status(500).json({ success: false, error: e.message });
    }
});

app.post('/agent/video', async (req, res) => {
    const { script, filename } = req.body;
    try {
        const file = await createVideo(script, filename || `video_${Date.now()}.mp4`);
        res.json({ success: true, url: `http://localhost:${PORT}/${file}` });
    } catch (e) {
        res.status(500).json({ success: false, error: e.message });
    }
});

app.listen(PORT, () => {
    console.log(`🕷️ Moltbot corriendo en puerto ${PORT}`);
});
