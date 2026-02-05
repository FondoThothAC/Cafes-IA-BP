const puppeteer = require('puppeteer-core');
const axios = require('axios');

// Config options (Same as server.js)
const IS_MAC = process.platform === 'darwin';
const PUPPETEER_OPTIONS = {
    executablePath: IS_MAC
        ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        : '/usr/bin/chromium-browser',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
};

const GATEWAY_API = process.env.IA_GATEWAY || 'http://host.docker.internal:3002';

async function deepResearch(topic, depth = 3) {
    console.log(`🧠 Iniciando Deep Research sobre: ${topic}`);

    // 1. Initial Search
    const searchResults = await searchWeb(topic);
    const topLinks = searchResults.slice(0, depth);

    let consolidatedInfo = `Research Report: ${topic}\n\n`;

    // 2. Deep Dive (Scrape each link)
    for (const link of topLinks) {
        try {
            console.log(`   - Leyendo: ${link.title}`);
            const content = await scrapePage(link.url);
            const summary = await summarizeContent(content, topic);

            consolidatedInfo += `## Source: ${link.title}\nURL: ${link.url}\n\n${summary}\n\n---\n\n`;
        } catch (e) {
            console.error(`Error reading ${link.url}: ${e.message}`);
        }
    }

    // 3. Final Synthesis
    const finalReport = await synthesizeReport(consolidatedInfo, topic);
    return finalReport;
}

// Helper: Web Search (DuckDuckGo Scraper)
async function searchWeb(query) {
    let browser = null;
    try {
        browser = await puppeteer.launch(PUPPETEER_OPTIONS);
        const page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36');

        await page.goto(`https://duckduckgo.com/?q=${encodeURIComponent(query)}&kl=mx-es`, { waitUntil: 'networkidle2', timeout: 30000 });

        return await page.evaluate(() => {
            const items = document.querySelectorAll('article');
            const data = [];
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
            return data;
        });
    } catch (e) {
        console.error("Search Error", e);
        return [];
    } finally {
        if (browser) await browser.close();
    }
}

// Helper: Scrape Page
async function scrapePage(url) {
    let browser = null;
    try {
        browser = await puppeteer.launch(PUPPETEER_OPTIONS);
        const page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36');
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });

        return await page.evaluate(() => document.body.innerText.substring(0, 8000));
    } catch (e) {
        return "Content extraction failed.";
    } finally {
        if (browser) await browser.close();
    }
}

// Helper: LLM Summarization
async function summarizeContent(text, topic) {
    try {
        const res = await axios.post(`${GATEWAY_API}/api/generate`, {
            prompt: `Resume en 3 puntos clave la información relevante sobre "${topic}" basada en este texto:\n\n${text.substring(0, 2000)}...`,
            source: 'moltbot-researcher'
        });
        return res.data.response || res.data.choices[0].text;
    } catch (e) {
        return "Could not summarize.";
    }
}

async function synthesizeReport(info, topic) {
    try {
        const res = await axios.post(`${GATEWAY_API}/api/generate`, {
            prompt: `Actúa como un Analista de Inteligencia. 
            Escribe un "Informe Ejecutivo" detallado sobre: "${topic}".
            Usa la siguiente investigación recopilada:
            
            ${info}
            
            Formato: Markdown profesional.
            Estructura: 
            1. Resumen Ejecutivo
            2. Hallazgos Clave
            3. Detalles por Fuente
            4. Conclusión`,
            source: 'moltbot-researcher'
        });
        return res.data.response || res.data.choices[0].text;
    } catch (e) {
        return info; // Fallback to raw info
    }
}

module.exports = { deepResearch };
