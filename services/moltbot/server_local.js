const express = require('express');
const cors = require('cors');
const puppeteer = require('puppeteer-core');
const { exec } = require('child_process');

const app = express();
const PORT = 8085;

app.use(cors());
app.use(express.json());

// Configuración de Puppeteer para macOS Local
const PUPPETEER_OPTIONS = {
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: 'new', // o false para ver el navegador
    args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions'
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
// ENDPOINT: OSINT (Sherlock) -> Dummy para local si no está instalado
// ==========================================
app.post('/osint/user', async (req, res) => {
    const { username } = req.body;
    if (!username) return res.status(400).json({ error: 'Username requerido' });

    console.log(`🔍 Buscando usuario (MOCK): ${username}`);

    // Simulación para prueba local
    res.json({
        success: true,
        username,
        found: 1,
        results: [
            { platform: 'Twitter', url: `https://twitter.com/${username}` },
            { platform: 'Instagram', url: `https://instagram.com/${username}` }
        ],
        note: "Ejecutando en modo local (Sherlock simulado)"
    });
});

app.listen(PORT, () => {
    console.log(`🕷️ Moltbot (Local) corriendo en http://localhost:${PORT}`);
});
