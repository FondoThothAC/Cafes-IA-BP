const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const DB_PATH = path.join(__dirname, 'audit.sqlite');
const SEARCH_JSON = path.join(__dirname, 'search_history.json');
const AI_JSON = path.join(__dirname, 'ai_history.json');

// Conectar a la base de datos (se crea si no existe)
const db = new sqlite3.Database(DB_PATH, (err) => {
    if (err) console.error('[DB] Error opening database:', err.message);
    else console.log('[DB] Connected to SQLite database.');
});

// Inicializar tablas
db.serialize(() => {
    // Tabla Historial de Búsquedas
    db.run(`CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user TEXT,
        type TEXT,
        query TEXT,
        location TEXT,
        results_count INTEGER,
        raw_data TEXT
    )`);

    // Tabla Historial IA
    db.run(`CREATE TABLE IF NOT EXISTS ai_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user TEXT,
        field_id TEXT,
        prompt TEXT,
        response TEXT
    )`);

    console.log('[DB] Tables initialized.');

    // Migración automática de JSON a SQLite
    migrateJsonData();
});

function migrateJsonData() {
    // Migrar Search History
    if (fs.existsSync(SEARCH_JSON)) {
        try {
            const data = JSON.parse(fs.readFileSync(SEARCH_JSON, 'utf8'));
            if (data.length > 0) {
                console.log(`[DB] Migrating ${data.length} search records...`);
                db.serialize(() => {
                    const stmt = db.prepare(`INSERT INTO search_history (timestamp, user, type, query, location, results_count) VALUES (?, ?, ?, ?, ?, ?)`);
                    let count = 0;
                    data.forEach(item => {
                        stmt.run(item.timestamp, item.user, item.type, item.query, item.location, item.resultsCount);
                        count++;
                    });
                    stmt.finalize();
                    console.log(`[DB] Migrated ${count} search records.`);
                });
            }
            fs.renameSync(SEARCH_JSON, SEARCH_JSON + '.bak');
            console.log('[DB] search_history.json renamed to .bak');
        } catch (e) {
            console.error('[DB] Error migrating search history:', e.message);
        }
    }

    // Migrar AI History
    if (fs.existsSync(AI_JSON)) {
        try {
            const data = JSON.parse(fs.readFileSync(AI_JSON, 'utf8'));
            if (data.length > 0) {
                console.log(`[DB] Migrating ${data.length} AI records...`);
                db.serialize(() => {
                    const stmt = db.prepare(`INSERT INTO ai_history (timestamp, user, field_id, prompt, response) VALUES (?, ?, ?, ?, ?)`);
                    let count = 0;
                    data.forEach(item => {
                        stmt.run(item.timestamp, item.user, item.fieldId, item.prompt, item.response);
                        count++;
                    });
                    stmt.finalize();
                    console.log(`[DB] Migrated ${count} AI records.`);
                });
            }
            fs.renameSync(AI_JSON, AI_JSON + '.bak');
            console.log('[DB] ai_history.json renamed to .bak');
        } catch (e) {
            console.error('[DB] Error migrating AI history:', e.message);
        }
    }
}

// Métodos de acceso a datos
module.exports = {
    db,

    insertSearch: (entry) => {
        return new Promise((resolve, reject) => {
            const sql = `INSERT INTO search_history (timestamp, user, type, query, location, results_count) VALUES (?, ?, ?, ?, ?, ?)`;
            const params = [new Date().toISOString(), entry.user, entry.type, entry.query, entry.location, entry.resultsCount];
            db.run(sql, params, function (err) {
                if (err) reject(err);
                else resolve({ id: this.lastID, ...entry });
            });
        });
    },

    insertAi: (entry) => {
        return new Promise((resolve, reject) => {
            const sql = `INSERT INTO ai_history (timestamp, user, field_id, prompt, response) VALUES (?, ?, ?, ?, ?)`;
            const params = [new Date().toISOString(), entry.user, entry.fieldId, entry.prompt, entry.response];
            db.run(sql, params, function (err) {
                if (err) reject(err);
                else resolve({ id: this.lastID, ...entry });
            });
        });
    },

    getSearchHistory: (limit = 100) => {
        return new Promise((resolve, reject) => {
            db.all(`SELECT * FROM search_history ORDER BY id DESC LIMIT ?`, [limit], (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    },

    getAiHistory: (limit = 50) => {
        return new Promise((resolve, reject) => {
            db.all(`SELECT * FROM ai_history ORDER BY id DESC LIMIT ?`, [limit], (err, rows) => {
                if (err) reject(err);
                else resolve(rows.map(row => ({
                    ...row,
                    fieldId: row.field_id // Mapping camelCase for frontend compatibility
                })));
            });
        });
    }
};
