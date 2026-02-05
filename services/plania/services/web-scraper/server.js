/**
 * =================================================================================
 * PROYECTO: PlanIA - Web Scraper Service
 * ARCHIVO: services/web-scraper/server.js
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: MIT
 * DESCRIPCIÓN: Servicio de búsqueda web y APIs públicas de México
 *              - Puppeteer: DuckDuckGo, Google Maps
 *              - APIs: INEGI, Banxico, Profeco
 * =================================================================================
 */

const express = require('express');
const cors = require('cors');
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const pdf = require('pdf-parse');

// KNOWLEDGE BASE CONFIG
const KB_DIR = path.join(__dirname, 'knowledge_base');
const upload = multer({ dest: KB_DIR });

const app = express();
const PORT = 3005;

// Módulo de Base de Datos SQLite
const db = require('./database');

app.use(cors());
app.use(express.json());
// Servir screenshots estáticos
app.use('/screenshots', express.static(path.join(__dirname, 'public/screenshots')));
// Servir directorio public para reportes y assets
app.use(express.static(path.join(__dirname, 'public')));

// =============================================================================
// SISTEMA DE HISTORIAL PERSISTENTE (SQLite)
// =============================================================================

/**
 * Registrar una búsqueda en el historial
 */
async function logSearch(entry) {
    try {
        const record = await db.insertSearch(entry);
        console.log(`[DB] Logged Search: ${entry.type} - ${entry.query}`);
        return record;
    } catch (e) { console.error('[DB] Error logging search:', e); }
}

/**
 * Registrar una interacción de IA
 */
async function logAiInteraction(entry) {
    try {
        const record = await db.insertAi(entry);
        console.log(`[DB] Logged AI: ${entry.fieldId} - User: ${entry.user}`);
        return record;
    } catch (e) { console.error('[DB] Error logging AI:', e); }
}

// =============================================================================
// DASHBOARD DE ADMINISTRADOR
// =============================================================================

// Página principal - Dashboard de historial
// Página principal - Dashboard de auditoría con Pestañas
// Página principal - Dashboard de auditoría con Pestañas
app.get('/', async (req, res) => {
    try {
        const history = await db.getSearchHistory(100);
        const aiHistory = await db.getAiHistory(50);

        // Stats Search (Calculado sobre los últimos 100 registros para simplicidad visual)
        // Idealmente esto sería un COUNT(*) en SQL
        const searchStats = {
            total: history.length, // Esto es solo del last 100, pero bueno para demo
            today: history.filter(h => h.timestamp?.startsWith(new Date().toISOString().split('T')[0])).length,
            byType: { competitors: 0, prices: 0 }
        };

        history.forEach(h => {
            if (h.type) {
                searchStats.byType[h.type] = (searchStats.byType[h.type] || 0) + 1;
            }
        });

        // Stats AI
        const aiStats = {
            total: aiHistory.length,
            today: aiHistory.filter(h => h.timestamp?.startsWith(new Date().toISOString().split('T')[0])).length
        };

        res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>PlanIA - Panel de Auditoría</title>
            <meta charset="UTF-8">
            <style>
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { font-family: 'Segoe UI', Arial, sans-serif; background: #0f0f23; color: #eee; }
                .header { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 20px 40px; border-bottom: 2px solid #00d9ff; display: flex; justify-content: space-between; align-items: center; }
                .header h1 { color: #00d9ff; font-size: 24px; }
                .tabs { display: flex; background: #16213e; padding: 0 40px; border-bottom: 1px solid #0f3460; }
                .tab { padding: 15px 30px; cursor: pointer; font-weight: bold; color: #888; border-bottom: 3px solid transparent; transition: all 0.3s; }
                .tab:hover { background: #1a2744; color: #ddd; }
                .tab.active { color: #00d9ff; border-bottom-color: #00d9ff; background: #0f3460; }
                
                .container { padding: 20px 40px; display: none; }
                .container.active { display: block; }
                
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .stat-card { background: #16213e; padding: 20px; border-radius: 12px; border-left: 4px solid #00d9ff; }
                .stat-card h3 { color: #888; font-size: 14px; margin-bottom: 8px; }
                .stat-card .value { font-size: 32px; font-weight: bold; color: #00d9ff; }
                
                table { width: 100%; border-collapse: collapse; background: #16213e; border-radius: 10px; overflow: hidden; font-size: 14px; }
                th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #0f3460; vertical-align: top; }
                th { background: #0f3460; color: #00d9ff; font-weight: 600; }
                tr:hover { background: #1a2744; }
                
                .badge { padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
                .badge-ai { background: #9b59b633; color: #9b59b6; }
                .badge-search { background: #3498db33; color: #3498db; }
                
                .expand-btn { cursor: pointer; color: #00d9ff; text-decoration: underline; font-size: 12px; }
                .full-text { display: none; white-space: pre-wrap; margin-top: 5px; background: #0a0a16; padding: 10px; border-radius: 5px; color: #ccc; }
                
                .filters { margin-bottom: 20px; display: flex; gap: 10px; }
                input { background: #16213e; border: 1px solid #0f3460; color: white; padding: 8px; border-radius: 4px; }
                button { background: #00d9ff; color: #000; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🕵️ PlanIA - Centro de Auditoría</h1>
                <div style="font-size: 14px; color: #888;">Puerto: ${PORT}</div>
            </div>
            
            <div class="tabs">
                <div class="tab active" onclick="switchTab('search')">🌍 Historial Búsquedas</div>
                <div class="tab" onclick="switchTab('ai')">🤖 Historial IA (Prompts)</div>
            </div>
            
            <!-- SEARCH TAB -->
            <div id="search-container" class="container active">
                <div class="stats">
                    <div class="stat-card"><h3>🔍 Total Búsquedas</h3><div class="value">${searchStats.total}</div></div>
                    <div class="stat-card"><h3>📅 Hoy</h3><div class="value">${searchStats.today}</div></div>
                    <div class="stat-card"><h3>🏢 Competidores</h3><div class="value">${searchStats.byType['competitors'] || 0}</div></div>
                    <div class="stat-card"><h3>💰 Precios</h3><div class="value">${searchStats.byType['prices'] || 0}</div></div>
                </div>
                
                <div class="filters" style="justify-content: flex-end; display: flex; margin-bottom: 10px;">
                    <button onclick="exportCSV('search')">📥 Exportar Búsquedas (CSV)</button>
                </div>
                
                <table id="searchTable">
                    <thead><tr><th>Hora</th><th>Usuario</th><th>Tipo</th><th>Consulta</th><th>Ubicación</th><th>Resultados</th></tr></thead>
                    <tbody>
                        ${history.slice(0, 100).map(h => `
                            <tr>
                                <td>${new Date(h.timestamp).toLocaleString()}</td>
                                <td>${h.user || 'anónimo'}</td>
                                <td><span class="badge badge-search">${h.type}</span></td>
                                <td>${h.query}</td>
                                <td>${h.location || '-'}</td>
                                <td>${h.resultsCount || 0}</td>
                            </tr>`).join('')}
                    </tbody>
                </table>
            </div>
            
            <!-- AI TAB -->
            <div id="ai-container" class="container">
                <div class="stats">
                    <div class="stat-card"><h3>🧠 Interacciones IA</h3><div class="value">${aiStats.total}</div></div>
                    <div class="stat-card"><h3>📅 Hoy</h3><div class="value">${aiStats.today}</div></div>
                </div>
                
                <div class="filters" style="justify-content: flex-end; display: flex; margin-bottom: 10px;">
                    <button onclick="exportCSV('ai')">📥 Exportar Auditoría IA (CSV)</button>
                </div>
                
                <table>
                    <thead><tr><th style="width:140px">Hora</th><th style="width:100px">Usuario</th><th>Campo</th><th>Prompt / Respuesta</th></tr></thead>
                    <tbody>
                        ${aiHistory.slice(0, 50).map((h, i) => `
                            <tr>
                                <td>${new Date(h.timestamp).toLocaleString()}</td>
                                <td>${h.user || 'anónimo'}</td>
                                <td><span class="badge badge-ai">${h.fieldId}</span></td>
                                <td>
                                    <div><strong>Prompt:</strong> ${h.prompt?.substring(0, 60)}... <span class="expand-btn" onclick="toggle('p-${i}')">ver más</span></div>
                                    <div id="p-${i}" class="full-text">${h.prompt}</div>
                                    
                                    <div style="margin-top:5px"><strong>Respuesta:</strong> ${h.response?.substring(0, 60)}... <span class="expand-btn" onclick="toggle('r-${i}')">ver más</span></div>
                                    <div id="r-${i}" class="full-text" style="color:#00ff88">${h.response}</div>
                                </td>
                            </tr>`).join('')}
                    </tbody>
                </table>
            </div>

            <script>
                function switchTab(tab) {
                    document.querySelectorAll('.container').forEach(c => c.classList.remove('active'));
                    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                    document.getElementById(tab + '-container').classList.add('active');
                    event.target.classList.add('active');
                }
                function toggle(id) {
                    const el = document.getElementById(id);
                    el.style.display = el.style.display === 'block' ? 'none' : 'block';
                }
                
                function exportCSV(type) {
                    const endpoint = type === 'ai' ? '/api/history/ai' : '/api/history';
                    fetch(endpoint)
                        .then(r => r.json())
                        .then(data => {
                            let csv = '';
                            if (type === 'ai') {
                                csv = 'Fecha,Usuario,Campo,Prompt,Respuesta\\n' + 
                                data.map(h => 
                                    '"' + [h.timestamp, h.user||'', h.fieldId||'', (h.prompt||'').replace(/"/g, '""'), (h.response||'').replace(/"/g, '""')].join('","') + '"'
                                ).join('\\n');
                            } else {
                                csv = 'Fecha,Usuario,Tipo,Busqueda,Ubicacion,Resultados\\n' + 
                                data.map(h => 
                                    '"' + [h.timestamp, h.user||'', h.type||'', (h.query||'').replace(/"/g, '""'), h.location||'', h.resultsCount||''].join('","') + '"'
                                ).join('\\n');
                            }
                            
                            const blob = new Blob([csv], {type: 'text/csv'});
                            const a = document.createElement('a');
                            a.href = URL.createObjectURL(blob);
                            a.download = 'plania_audit_' + type + '_' + new Date().toISOString().split('T')[0] + '.csv';
                            a.click();
                        });
                }
            </script>
        </body>
        </html>
    `);
    } catch (e) {
        res.status(500).send('Error loading dashboard: ' + e.message);
    }
});

/**
 * POST /audit/ai - Endpoint para registrar interacciones de IA
 */
app.post('/audit/ai', (req, res) => {
    const { user, fieldId, prompt, response } = req.body;
    logAiInteraction({ user, fieldId, prompt, response });
    res.json({ success: true });
});

// API para obtener historial en JSON (Search)
app.get('/api/history', async (req, res) => {
    try {
        const history = await db.getSearchHistory(1000);
        res.json(history);
    } catch (e) { res.status(500).json({ error: e.message }); }
});

// API para obtener historial en JSON (AI)
app.get('/api/history/ai', async (req, res) => {
    try {
        // Obtenemos historial AI (sin límite para exportación completa o límite alto)
        const history = await db.getAiHistory(1000);
        res.json(history);
    } catch (e) { res.status(500).json({ error: e.message }); }
});

// Endpoint de borrado deshabilitado por seguridad en migración SQLite
// app.delete('/api/history', ...);

// Browser instance (reutilizable)
let browser = null;

async function getBrowser() {
    if (!browser) {
        // Try to find Chrome on macOS
        const chromePaths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium',
            process.env.CHROME_PATH
        ].filter(Boolean);

        let executablePath = null;
        for (const path of chromePaths) {
            try {
                const fs = require('fs');
                if (fs.existsSync(path)) {
                    executablePath = path;
                    break;
                }
            } catch (e) { }
        }

        const launchOptions = {
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920,1080'
            ]
        };

        if (executablePath) {
            launchOptions.executablePath = executablePath;
            console.log('[Scraper] Using Chrome at:', executablePath);
        } else {
            console.log('[Scraper] Using bundled Chromium');
        }

        try {
            browser = await puppeteer.launch(launchOptions);
            console.log('[Scraper] Browser launched successfully');
        } catch (error) {
            console.error('[Scraper] Failed to launch browser:', error.message);
            throw error;
        }
    }
    return browser;
}

// =============================================================================
// APIs GRATUITAS DE MÉXICO
// =============================================================================

/**
 * INEGI API - Indicadores Económicos
 * Documentación: https://www.inegi.org.mx/servicios/api_indicadores.html
 * Token público disponible en: https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/CL_AREA_GEO.html
 */
async function getINEGIIndicators(indicator = 'inflacion') {
    // IDs de indicadores verificados del BIE
    const indicators = {
        'inflacion': '628194',        // INPC Inflación mensual
        'pib': '493911',              // PIB trimestral
        'desempleo': '444612',        // Tasa de desocupación
        'poblacion': '1002000001',    // Población total
        'salario_minimo': '1005000023' // Salario mínimo general
    };

    const indicatorId = indicators[indicator] || indicators['inflacion'];

    try {
        // INEGI API pública - formato correcto con token público
        // El token "INEGI" es un token de prueba público
        const url = `https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/${indicatorId}/es/0700/false/BIE/2.0/INEGI?type=json`;

        console.log('[INEGI API] Fetching:', url);

        const response = await fetch(url, {
            signal: AbortSignal.timeout(10000),
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            console.error('[INEGI API] Response not ok:', response.status);
            throw new Error(`INEGI API error: ${response.status}`);
        }

        const data = await response.json();

        if (data.Series && data.Series[0]) {
            const serie = data.Series[0];
            const observations = serie.OBSERVATIONS || [];
            const latest = observations[observations.length - 1];

            return {
                indicator: serie.INDICADOR || indicator,
                value: latest?.OBS_VALUE || 'N/A',
                period: latest?.TIME_PERIOD || 'N/A',
                unit: serie.UNIT || '',
                source: 'INEGI API'
            };
        }

        return null;
    } catch (error) {
        console.error('[INEGI API] Error:', error.message);
        // Fallback con datos estáticos de referencia
        return {
            indicator: indicator,
            value: indicator === 'inflacion' ? '4.2%' : 'N/A',
            period: '2024',
            unit: '%',
            source: 'INEGI (estimado)'
        };
    }
}

/**
 * Banxico API SIE - Sistema de Información Económica
 * Documentación: https://www.banxico.org.mx/SieAPIRest/service/v1/
 * NOTA: Requiere token. Usando endpoint alternativo público.
 */
async function getBanxicoData(seriesId = 'tipo_cambio') {
    const series = {
        'tipo_cambio': 'SF43718',    // USD/MXN FIX
        'tiie_28': 'SF60649',        // TIIE 28 días
        'cetes_28': 'SF60634',       // CETES 28 días
        'udis': 'SP68257',           // Valor UDI
        'inflacion': 'SP74625'       // Inflación interanual
    };

    const id = series[seriesId] || series['tipo_cambio'];

    try {
        // Usar endpoint público de datos oportunos (no requiere token para datos básicos)
        // Endpoint alternativo que sí funciona sin token
        const url = `https://www.banxico.org.mx/SieAPIRest/service/v1/series/${id}/datos/oportuno`;

        console.log('[Banxico API] Fetching:', url);

        const response = await fetch(url, {
            headers: {
                'Accept': 'application/json',
                // Token de ejemplo - el usuario puede solicitar uno propio gratis
                'Bmx-Token': process.env.BANXICO_TOKEN || ''
            },
            signal: AbortSignal.timeout(10000)
        });

        // Si no tenemos token válido, usar datos de scraping como fallback
        if (!response.ok) {
            console.log('[Banxico API] No token, using fallback');
            return await getBanxicoFallback(seriesId);
        }

        const data = await response.json();

        if (data.bmx && data.bmx.series && data.bmx.series[0]) {
            const serie = data.bmx.series[0];
            const latest = serie.datos[0];

            return {
                title: serie.titulo || seriesId,
                value: latest?.dato || 'N/A',
                date: latest?.fecha || 'N/A',
                source: 'Banxico API'
            };
        }

        return await getBanxicoFallback(seriesId);
    } catch (error) {
        console.error('[Banxico API] Error:', error.message);
        return await getBanxicoFallback(seriesId);
    }
}

/**
 * Fallback: Obtener tipo de cambio de APIs gratuitas o scraping
 */
async function getBanxicoFallback(seriesId) {
    console.log('[Banxico Fallback] Getting exchange rate from free sources...');

    // Opción 1: API gratuita de ExchangeRate-API (no requiere token)
    try {
        const response = await fetch('https://open.er-api.com/v6/latest/USD', {
            signal: AbortSignal.timeout(8000)
        });

        if (response.ok) {
            const data = await response.json();
            if (data.rates && data.rates.MXN) {
                console.log('[ExchangeRate API] Success:', data.rates.MXN);
                return {
                    title: 'Tipo de Cambio USD/MXN',
                    value: data.rates.MXN.toFixed(2),
                    date: data.time_last_update_utc?.split(' ').slice(0, 4).join(' ') || new Date().toLocaleDateString('es-MX'),
                    source: 'ExchangeRate API'
                };
            }
        }
    } catch (e) {
        console.log('[ExchangeRate API] Error:', e.message);
    }

    // Opción 2: Scraping de Google
    try {
        const browser = await getBrowser();
        const page = await browser.newPage();

        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');
        await page.goto('https://www.google.com/search?q=USD+to+MXN', {
            waitUntil: 'domcontentloaded',
            timeout: 10000
        });

        const result = await page.evaluate(() => {
            // Google muestra el tipo de cambio en un div especial
            const rateEl = document.querySelector('[data-value], .DFlfde, .SwHCTb');
            if (rateEl) {
                const value = rateEl.getAttribute('data-value') || rateEl.textContent?.trim();
                return value ? parseFloat(value) : null;
            }
            return null;
        });

        await page.close();

        if (result) {
            return {
                title: 'Tipo de Cambio USD/MXN',
                value: result.toFixed(2),
                date: new Date().toLocaleDateString('es-MX'),
                source: 'Google Finance'
            };
        }
    } catch (e) {
        console.log('[Google Finance] Error:', e.message);
    }

    // Fallback final: valor aproximado actualizado
    return {
        title: 'Tipo de Cambio USD/MXN',
        value: '20.50',
        date: new Date().toLocaleDateString('es-MX'),
        source: 'Referencia (actualizar manualmente)'
    };
}

/**
 * Profeco - Quién es Quién en los Precios (scraping)
 * Para comparar precios de productos
 */
async function searchProfecoPrecios(product) {
    const browser = await getBrowser();
    const page = await browser.newPage();

    try {
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');
        await page.goto(`https://www.profeco.gob.mx/precios/canasta/home.aspx?th=1&q=${encodeURIComponent(product)}`, {
            waitUntil: 'networkidle2',
            timeout: 15000
        });

        await page.waitForSelector('.precio-item, .resultado', { timeout: 8000 }).catch(() => { });

        const results = await page.evaluate(() => {
            const items = document.querySelectorAll('.precio-item, tr.resultado');
            const data = [];

            items.forEach((item, i) => {
                if (i >= 5) return;

                const producto = item.querySelector('.producto, td:first-child')?.textContent?.trim();
                const precio = item.querySelector('.precio, td.precio')?.textContent?.trim();
                const tienda = item.querySelector('.tienda, td.establecimiento')?.textContent?.trim();

                if (producto && precio) {
                    data.push({
                        producto,
                        precio,
                        tienda: tienda || 'N/A',
                        source: 'Profeco'
                    });
                }
            });

            return data;
        });

        return results;
    } catch (error) {
        console.error('[Profeco] Error:', error.message);
        return [];
    } finally {
        await page.close();
    }
}

/**
 * MercadoLibre - Precios de referencia (scraping)
 */
async function searchMercadoLibrePrecios(product, category = '') {
    const browser = await getBrowser();
    const page = await browser.newPage();

    try {
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');
        await page.goto(`https://listado.mercadolibre.com.mx/${encodeURIComponent(product)}`, {
            waitUntil: 'networkidle2',
            timeout: 15000
        });

        await page.waitForSelector('.ui-search-result__wrapper', { timeout: 8000 }).catch(() => { });

        const results = await page.evaluate(() => {
            const items = document.querySelectorAll('.ui-search-result__wrapper');
            const data = [];
            let totalPrice = 0;
            let count = 0;

            items.forEach((item, i) => {
                if (i >= 10) return;

                const titleEl = item.querySelector('.ui-search-item__title');
                const priceEl = item.querySelector('.andes-money-amount__fraction');

                if (titleEl && priceEl) {
                    const price = parseInt(priceEl.textContent.replace(/[,\.]/g, '')) || 0;
                    if (price > 0) {
                        totalPrice += price;
                        count++;
                    }

                    if (i < 5) {
                        data.push({
                            producto: titleEl.textContent?.trim(),
                            precio: `$${priceEl.textContent}`,
                            source: 'MercadoLibre'
                        });
                    }
                }
            });

            return {
                items: data,
                averagePrice: count > 0 ? Math.round(totalPrice / count) : null,
                sampleSize: count
            };
        });

        return results;
    } catch (error) {
        console.error('[MercadoLibre] Error:', error.message);
        return { items: [], averagePrice: null };
    } finally {
        await page.close();
    }
    /**
     * CONSULTA SNIIM (Sistema Nacional de Información e Integración de Mercados)
     * Agrícolas, Pecuarios, etc.
     */
    async function searchSNIIM(product) {
        console.log(`[SNIIM] Buscando: ${product}`);
        const browser = await getBrowser();
        const page = await browser.newPage();
        try {
            await page.goto(`https://www.google.com/search?q=site:economia-sniim.gob.mx+precio+${encodeURIComponent(product)}`, { waitUntil: 'networkidle2' });
            const results = await page.evaluate(() => {
                const data = [];
                document.querySelectorAll('.g').forEach(el => {
                    const title = el.querySelector('h3')?.innerText;
                    const snippet = el.querySelector('.VwiC3b')?.innerText;
                    if (title && snippet) {
                        const priceMatch = snippet.match(/\$\s?(\d+(?:\.\d{2})?)/);
                        data.push({
                            product: title.replace(' - SNIIM', ''),
                            price: priceMatch ? parseFloat(priceMatch[1]) : null,
                            source: 'SNIIM (via Google)',
                            date: new Date().toISOString().split('T')[0]
                        });
                    }
                });
                return data;
            });
            return results.filter(r => r.price !== null);
        } catch (error) {
            console.error('[SNIIM] Error:', error);
            return [];
        } finally {
            await page.close();
        }
    }

    /**
     * Búsqueda Generica de Supermercados
     * (Walmart, Soriana, Chedraui via Google Shopping)
     */
    async function searchSupermarkets(product) {
        const browser = await getBrowser();
        const page = await browser.newPage();
        try {
            await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
            const query = encodeURIComponent(product);
            await page.goto(`https://www.google.com/search?q=${query}&tbm=shop`, { waitUntil: 'networkidle2' });
            const results = await page.evaluate(() => {
                const items = [];
                document.querySelectorAll('.sh-dgr__content').forEach(el => {
                    const title = el.querySelector('h3')?.innerText;
                    const priceText = el.querySelector('.a8Pemb')?.innerText || el.querySelector('.HL4Sgs')?.innerText;
                    const merchant = el.querySelector('.aULzUe')?.innerText || el.querySelector('.IuHnof')?.innerText;
                    if (title && priceText) {
                        const price = parseFloat(priceText.replace(/[^0-9.]/g, ''));
                        items.push({
                            title,
                            price,
                            merchant: merchant || 'Desconocido',
                            currency: 'MXN'
                        });
                    }
                });
                return items.slice(0, 10);
            });
            return results;
        } catch (e) {
            console.error('[Supermarkets] Error:', e);
            return [];
        } finally {
            await page.close();
        }
    }
    async function searchDENUE(activity, state = '') {
        const browser = await getBrowser();
        const page = await browser.newPage();

        try {
            await page.goto(`https://www.inegi.org.mx/app/mapa/denue/default.aspx`, {
                waitUntil: 'networkidle2',
                timeout: 20000
            });

            // El DENUE requiere interacción, hacer búsqueda simple
            const searchUrl = `https://www.inegi.org.mx/app/buscador/default.html?q=denue+${encodeURIComponent(activity)}+${encodeURIComponent(state)}`;
            await page.goto(searchUrl, { waitUntil: 'networkidle2' });

            await page.waitForSelector('.resultado', { timeout: 8000 }).catch(() => { });

            const results = await page.evaluate(() => {
                const items = document.querySelectorAll('.resultado');
                const data = [];

                items.forEach((item, i) => {
                    if (i >= 3) return;

                    const titleEl = item.querySelector('h3 a');
                    const descEl = item.querySelector('.descripcion');

                    if (titleEl) {
                        data.push({
                            title: titleEl.textContent?.trim() || '',
                            url: titleEl.href || '',
                            description: descEl?.textContent?.trim() || '',
                            source: 'DENUE/INEGI'
                        });
                    }
                });

                return data;
            });

            return results;
        } catch (error) {
            console.error('[DENUE] Error:', error.message);
            return [];
        } finally {
            await page.close();
        }
    }

    // =============================================================================
    // FUNCIONES ORIGINALES (mantenidas)
    // =============================================================================

    /**
     * Buscar en DuckDuckGo (sin límites de API)
     */
    async function searchDuckDuckGo(query, maxResults = 5, region = 'mx-es') {
        const browser = await getBrowser();
        const page = await browser.newPage();

        try {
            await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');
            const regionParam = region ? `&kl=${region}` : '';
            await page.goto(`https://duckduckgo.com/?q=${encodeURIComponent(query)}&ia=web${regionParam}`, {
                waitUntil: 'networkidle2',
                timeout: 15000
            });

            await page.waitForSelector('[data-testid="result"]', { timeout: 10000 }).catch(() => { });

            const results = await page.evaluate((max) => {
                // 1. Try to get Instant Answer (Calculator/Converter/Zero-Click Info)
                const answerEl = document.querySelector('.c-base__title') ||
                    document.querySelector('#zci-result') ||
                    document.querySelector('.zci__def__text') ||
                    document.querySelector('.module__content .module__title'); // Generic

                const answerSub = document.querySelector('.c-base__sub') ||
                    document.querySelector('.zci__def__sub') ||
                    document.querySelector('.module__content .module__text'); // Generic

                let instantAnswer = null;
                if (answerEl) {
                    instantAnswer = {
                        title: "Respuesta Rápida (Instant Answer)",
                        url: "https://duckduckgo.com",
                        snippet: "DATOS EXACTOS (TOP RESULT): " + answerEl.innerText + (answerSub ? " " + answerSub.innerText : "")
                    };
                }

                // 2. Standard Results
                const items = document.querySelectorAll('[data-testid="result"]');
                const data = [];

                if (instantAnswer) {
                    data.push(instantAnswer);
                }

                items.forEach((item, i) => {
                    if (data.length >= max + (instantAnswer ? 1 : 0)) return;

                    const titleEl = item.querySelector('h2 a');
                    const snippetEl = item.querySelector('[data-result="snippet"]');

                    if (titleEl) {
                        data.push({
                            title: titleEl.textContent?.trim() || '',
                            url: titleEl.href || '',
                            snippet: snippetEl?.textContent?.trim() || ''
                        });
                    }
                });

                return data;
            }, maxResults);

            return results;
        } catch (error) {
            console.error('[DuckDuckGo] Error:', error.message);
            return [];
        } finally {
            await page.close();
        }
    }

    /**
     * Buscar competidores en Google Maps
     */
    async function searchGoogleMaps(query, location = '') {
        const browser = await getBrowser();
        const page = await browser.newPage();

        try {
            const searchQuery = location ? `${query} near ${location}` : query;
            await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');
            await page.goto(`https://www.google.com/maps/search/${encodeURIComponent(searchQuery)}`, {
                waitUntil: 'networkidle2',
                timeout: 20000
            });

            await page.waitForSelector('[role="feed"]', { timeout: 10000 }).catch(() => { });
            await new Promise(r => setTimeout(r, 2000));

            const results = await page.evaluate(() => {
                const items = document.querySelectorAll('[role="feed"] > div > div > a');
                const data = [];

                items.forEach((item, i) => {
                    if (i >= 5) return;

                    const name = item.getAttribute('aria-label');
                    const href = item.href;

                    if (name) {
                        data.push({
                            name: name,
                            url: href,
                            source: 'Google Maps'
                        });
                    }
                });

                return data;
            });

            return results;
        } catch (error) {
            console.error('[GoogleMaps] Error:', error.message);
            return [];
        } finally {
            await page.close();
        }
    }

    // =============================================================================
    // API ENDPOINTS
    // =============================================================================

    /**
     * POST /search - Búsqueda general
     */
    app.post('/search', async (req, res) => {
        const { query, type = 'general', location = '', maxResults = 5, user = '' } = req.body;

        console.log(`[API] Search: "${query}" type=${type}`);

        try {
            let results = [];

            switch (type) {
                case 'competitors':
                    results = await searchGoogleMaps(query, location);
                    break;
                case 'statistics':
                    const denue = await searchDENUE(query, location);
                    results = denue;
                    break;
                case 'prices':
                    const mlResults = await searchMercadoLibrePrecios(query);
                    results = mlResults.items;
                    results.averagePrice = mlResults.averagePrice;
                    break;
                case 'general':
                default:
                    // Enhancement: Check for currency queries to inject reliable API data
                    const loweredQuery = query.toLowerCase();
                    const currencyKeywords = ['dolar', 'dólar', 'usd', 'peso', 'cambio', 'moneda'];

                    // Extract region from request or default to Mexico (mx-es) if not specified
                    // DuckDuckGo regions: mx-es, us-en, cn-zh, ru-ru, fr-fr, etc.
                    const regionParam = req.body.region || 'mx-es';

                    results = await searchDuckDuckGo(query, maxResults, regionParam);

                    if (currencyKeywords.some(kw => loweredQuery.includes(kw))) {
                        try {
                            console.log('[API] Detected currency query, fetching Banxico/API data...');
                            const currencyData = await getBanxicoData('tipo_cambio');
                            if (currencyData && currencyData.value) {
                                results.unshift({
                                    title: `💰 ${currencyData.title} (Oficial/API)`,
                                    url: "https://www.banxico.org.mx/",
                                    snippet: `DATOS OFICIALES (${currencyData.date}): El tipo de cambio es de $${currencyData.value} MXN por USD. Fuente: ${currencyData.source}.`
                                });
                            }
                        } catch (e) {
                            console.error('[API] Failed to inject currency data:', e);
                        }
                    }
                    break;
            }

            // Registrar en historial
            logSearch({
                type,
                query,
                location,
                user: user || req.headers['x-user-id'] || 'anónimo',
                resultsCount: Array.isArray(results) ? results.length : 0
            });

            res.json({ success: true, results, query, type });
        } catch (error) {
            console.error('[API] Error:', error);
            res.status(500).json({ success: false, error: error.message });
        }
    });

    // Endpoint para productos agrícolas (SNIIM)
    app.post('/prices/agriculture', async (req, res) => {
        const { product } = req.body;
        if (!product) return res.status(400).json({ error: 'Product is required' });
        try {
            const results = await searchSNIIM(product);
            await logSearch({ type: 'sniim', query: product, results: results.length });
            res.json({ success: true, data: results });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });

    // Endpoint para retail (Supermercados)
    app.post('/prices/retail', async (req, res) => {
        const { product } = req.body;
        if (!product) return res.status(400).json({ error: 'Product is required' });
        try {
            const results = await searchSupermarkets(product);
            await logSearch({ type: 'retail', query: product, results: results.length });
            res.json({ success: true, data: results });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });

    /**
     * GET /indicators - Indicadores económicos de México
     */
    app.get('/indicators', async (req, res) => {
        console.log('[API] Getting economic indicators');

        try {
            const [inegi, banxico] = await Promise.all([
                getINEGIIndicators('desempleo'),
                getBanxicoData('tipo_cambio')
            ]);

            res.json({
                success: true,
                indicators: {
                    inegi,
                    banxico,
                    timestamp: new Date().toISOString()
                }
            });
        } catch (error) {
            console.error('[API] Indicators error:', error);
            res.status(500).json({ success: false, error: error.message });
        }
    });

    /**
     * POST /prices - Comparar precios de productos
     */
    app.post('/prices', async (req, res) => {
        const { product } = req.body;

        console.log(`[API] Price search: "${product}"`);

        try {
            const [mercadoLibre, profeco] = await Promise.all([
                searchMercadoLibrePrecios(product),
                searchProfecoPrecios(product)
            ]);

            // Registrar en historial
            logSearch({
                type: 'prices',
                query: product,
                resultsCount: (mercadoLibre.items?.length || 0) + (profeco?.length || 0),
                user: req.body.user || 'anónimo'
            });

            res.json({
                success: true,
                product,
                data: {
                    mercadoLibre: {
                        items: mercadoLibre.items,
                        averagePrice: mercadoLibre.averagePrice,
                        sampleSize: mercadoLibre.sampleSize
                    },
                    profeco: profeco
                }
            });
        } catch (error) {
            console.error('[API] Prices error:', error);
            res.status(500).json({ success: false, error: error.message });
        }
    });

    /**
     * POST /research - Investigación completa para un negocio
     */
    app.post('/research', async (req, res) => {
        const { businessName, industry, location } = req.body;

        console.log(`[API] Research: "${businessName}" in ${industry}`);

        try {
            // Búsquedas paralelas
            const [competitors, marketInfo, indicators] = await Promise.all([
                searchGoogleMaps(`${industry} ${location}`, location),
                searchDuckDuckGo(`${industry} mercado tendencias México 2024`, 3),
                Promise.all([
                    getINEGIIndicators('empresas'),
                    getBanxicoData('tipo_cambio')
                ])
            ]);

            // Registrar en historial
            logSearch({
                type: 'research',
                query: `${businessName} - ${industry}`,
                location,
                resultsCount: 1, // Resultado complejo
                user: req.body.user || 'anónimo'
            });

            res.json({
                success: true,
                businessName,
                data: {
                    competitors,
                    marketInfo,
                    economicIndicators: {
                        inegi: indicators[0],
                        banxico: indicators[1]
                    }
                }
            });
        } catch (error) {
            console.error('[API] Research error:', error);
            res.status(500).json({ success: false, error: error.message });
        }
    });
    /**
     * POST /capture-map - Capturar screenshot de Google Maps
     */
    app.post('/capture-map', async (req, res) => {
        const { query, user } = req.body;
        console.log(`[API] Capturing Map: "${query}"`);

        try {
            const browser = await getBrowser();
            const page = await browser.newPage();
            await page.setViewport({ width: 1280, height: 720 });

            // Navegar a Google Maps
            // Usamos una URL de embed o search limpia
            await page.goto(`https://www.google.com/maps/search/${encodeURIComponent(query)}?hl=es`, { waitUntil: 'networkidle2' });

            // Esperar carga visual extra
            await new Promise(r => setTimeout(r, 3000));

            const filename = `map_${Date.now()}.jpg`;
            const filepath = path.join(__dirname, 'public/screenshots', filename);

            await page.screenshot({ path: filepath, type: 'jpeg', quality: 85 });
            await page.close();

            // Log auditoría
            await logSearch({
                type: 'map_capture',
                query: query,
                location: 'Screenshot',
                resultsCount: 1,
                user: user || 'system'
            });

            console.log(`[Capture] Saved to ${filepath}`);
            res.json({ success: true, url: `http://localhost:${PORT}/screenshots/${filename}` });
        } catch (e) {
            console.error('[Capture] Error:', e);
            res.status(500).json({ error: e.message });
        }
    });
    /**
     * GET /health - Health check
     */
    app.get('/health', (req, res) => {
        res.json({
            status: 'ok',
            service: 'PlanIA Web Scraper + APIs México',
            port: PORT,
            sources: ['DuckDuckGo', 'Google Maps', 'INEGI API', 'Banxico API', 'Profeco', 'MercadoLibre', 'DENUE']
        });
    });

    // Cleanup on exit
    process.on('SIGINT', async () => {
        if (browser) {
            await browser.close();
        }
        process.exit();
    });

    // =============================================================================
    // KNOWLEDGE BASE (RAG) - LOCAL FILES
    // =============================================================================

    app.post('/knowledge/upload', upload.single('file'), async (req, res) => {
        try {
            if (!req.file) return res.status(400).json({ success: false, error: 'No file uploaded' });

            const originalName = req.file.originalname;
            const filePath = req.file.path;
            console.log(`[KB] File uploaded: ${originalName}`);

            // Extract Text if PDF
            let textContent = '';
            if (req.file.mimetype === 'application/pdf' || originalName.toLowerCase().endsWith('.pdf')) {
                try {
                    const dataBuffer = fs.readFileSync(filePath);
                    const pdfData = await pdf(dataBuffer);
                    textContent = pdfData.text;
                } catch (err) {
                    console.error('Error parsing PDF:', err);
                    textContent = '[Error reading PDF content]';
                }
            } else {
                // Assume text/md
                textContent = fs.readFileSync(filePath, 'utf8');
            }

            // Save Extracted Text as .txt metadata
            const metaPath = filePath + '.txt';
            fs.writeFileSync(metaPath, textContent);

            // Save Metadata JSON
            const jsonPath = filePath + '.json';
            const meta = {
                id: req.file.filename,
                originalName: originalName,
                mimetype: req.file.mimetype,
                size: req.file.size,
                uploadDate: new Date().toISOString(),
                txtPath: metaPath
            };
            fs.writeFileSync(jsonPath, JSON.stringify(meta));

            res.json({ success: true, file: meta });

        } catch (e) {
            console.error('[KB] Upload Error:', e);
            res.status(500).json({ success: false, error: e.message });
        }
    });

    app.get('/knowledge/list', (req, res) => {
        try {
            if (!fs.existsSync(KB_DIR)) fs.mkdirSync(KB_DIR);
            const files = fs.readdirSync(KB_DIR).filter(f => f.endsWith('.json'));
            const docs = files.map(f => {
                try {
                    const content = fs.readFileSync(path.join(KB_DIR, f), 'utf8');
                    return JSON.parse(content);
                } catch (e) { return null; }
            }).filter(d => d !== null);
            res.json({ success: true, documents: docs });
        } catch (e) {
            res.status(500).json({ success: false, error: e.message });
        }
    });

    app.post('/knowledge/scrape', async (req, res) => {
        let internalBrowser;
        try {
            const { url } = req.body;
            if (!url) return res.status(400).json({ success: false, error: 'URL is required' });

            console.log(`[KB] Scraping to Knowledge Base: ${url}`);

            // 1. Launch Puppeteer to get clean text
            internalBrowser = await puppeteer.launch({ headless: 'new' });
            const page = await internalBrowser.newPage();
            await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

            const title = await page.title();
            const textContent = await page.evaluate(() => document.body.innerText);

            // 2. Save to KB folder
            const id = 'scrape_' + Date.now();
            const fileName = `${id}.txt`;
            const jsonName = `${id}.json`;

            fs.writeFileSync(path.join(KB_DIR, fileName), textContent);

            const meta = {
                id: id,
                originalName: `🌐 ${title || url}`,
                mimetype: 'text/plain',
                size: textContent.length,
                uploadDate: new Date().toISOString(),
                url: url
            };
            fs.writeFileSync(path.join(KB_DIR, jsonName), JSON.stringify(meta));

            res.json({ success: true, file: meta });

        } catch (e) {
            console.error('[KB] Scrape Error:', e);
            res.status(500).json({ success: false, error: e.message });
        } finally {
            if (internalBrowser) await internalBrowser.close();
        }
    });

    app.post('/knowledge/context', (req, res) => {
        try {
            const { docIds } = req.body;
            if (!docIds || !Array.isArray(docIds)) return res.json({ success: false, context: '' });

            let context = '';
            docIds.forEach(id => {
                // id is filename without extension (multer id)
                // But we stored it in meta.id
                const txtPath = path.join(KB_DIR, id + '.txt');
                const jsonPath = path.join(KB_DIR, id + '.json');

                if (fs.existsSync(txtPath) && fs.existsSync(jsonPath)) {
                    const meta = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
                    let text = fs.readFileSync(txtPath, 'utf8');
                    // Truncate
                    if (text.length > 15000) text = text.substring(0, 15000) + '... (truncado)';
                    context += `\n>>> FUENTE: ${meta.originalName} <<<\n${text}\n----------------------------------\n`;
                }
            });
            res.json({ success: true, context });
        } catch (e) {
            res.status(500).json({ success: false, error: e.message });
        }
    });

    // =============================================================================
    // OLLAMA PROXY (Para evitar CORS desde el navegador)
    // =============================================================================
    app.post('/api/ollama-proxy', async (req, res) => {
        try {
            const { prompt, model = 'gemma3:1b', stream = false } = req.body;

            // Forward to local Ollama
            const ollamaUrl = process.env.OLLAMA_HOST || 'http://localhost:11434';
            const response = await fetch(`${ollamaUrl}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, model, stream })
            });

            if (!response.ok) {
                throw new Error(`Ollama returned ${response.status}`);
            }

            const data = await response.json();
            res.json(data);
        } catch (error) {
            console.error('[Ollama Proxy Error]', error.message);
            res.status(500).json({ error: error.message, response: null });
        }
    });

    app.listen(PORT, () => {
        console.log(`
╔═══════════════════════════════════════════════════╗
║  PlanIA Web Scraper + APIs México Service         ║
║  Running on http://localhost:${PORT}                 ║
╠═══════════════════════════════════════════════════╣
║  Fuentes disponibles:                             ║
║  • DuckDuckGo    - Búsqueda general               ║
║  • Google Maps   - Competidores locales           ║
║  • INEGI API     - Indicadores económicos         ║
║  • Banxico API   - Datos financieros              ║
║  • Profeco       - Precios (Quién es Quién)       ║
║  • MercadoLibre  - Precios de referencia          ║
║  • DENUE         - Directorio de empresas         ║
╚═══════════════════════════════════════════════════╝
    `);
    });
