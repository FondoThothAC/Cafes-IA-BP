/**
 * =================================================================================
 * PROYECTO: PlanIA (Frontend - Import Client)
 * ARCHIVO: public/js/import-client.js
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: MIT
 * DESCRIPCIÓN: Cliente para importar documentos escaneados/PDFs 
 *              y mapearlos al formulario.
 * =================================================================================
 */

class ImportClient {
    constructor() {
        // Detectar host dinámicamente para soportar acceso remoto
        const host = window.location.hostname;
        const gatewayPort = 3002;
        this.ocrUrl = `http://${host}:${gatewayPort}/api/agent/ocr-upload`;
        this.backendUrl = `http://${host}:${gatewayPort}/api/agent/ocr-map`;
        this.currentMapping = null;
    }

    /**
     * Inicializa el modal y los event listeners
     */
    init() {
        this.createModal();
        this.checkPendingImport();
        console.log('📄 Import Client initialized');
    }

    createModal() {
        // Verificar si ya existe
        if (document.getElementById('importModal')) return;

        const modalHtml = `
            <div id="importModal" class="modal-overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 2000; justify-content: center; align-items: center;">
                <div class="modal-content" style="background: var(--surface); width: 600px; max-width: 90%; padding: 2rem; border-radius: 12px; position: relative; max-height: 90vh; overflow-y: auto;">
                    <button onclick="document.getElementById('importModal').style.display='none'" style="position: absolute; top: 15px; right: 15px; background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer;">&times;</button>
                    
                    <div style="text-align: center; margin-bottom: 2rem;">
                        <span style="font-size: 3rem;">📄</span>
                        <h2 style="margin: 0.5rem 0;">Importar Documento</h2>
                        <p style="color: var(--text-muted);">Sube una foto o PDF de tu cuestionario o plan anterior.</p>
                    </div>

                    <div id="uploadStep">
                        <div class="drop-zone" id="dropZone" style="border: 2px dashed var(--surface-light); border-radius: 8px; padding: 3rem 1rem; text-align: center; cursor: pointer; transition: all 0.2s;">
                            <p style="margin: 0; color: var(--text-muted);">Arrastra tu archivo aquí o haz clic para seleccionar</p>
                            <input type="file" id="fileInput" accept="image/*,.pdf" style="display: none;">
                        </div>
                        <p style="font-size: 0.8rem; color: var(--text-muted); text-align: center; margin-top: 1rem;">Formatos: JPG, PNG, PDF (Máx 10MB)</p>
                    </div>

                    <div id="processingStep" style="display: none; text-align: center; padding: 2rem;">
                        <div class="spinner" style="width: 40px; height: 40px; border: 4px solid var(--surface-light); border-top: 4px solid var(--primary); border-radius: 50%; margin: 0 auto 1rem; animation: spin 1s linear infinite;"></div>
                        <h3 id="processStatus">Leyendo documento...</h3>
                        <p style="color: var(--text-muted);">Usando OCR e IA para identificar campos</p>
                    </div>

                    <div id="previewStep" style="display: none;">
                        <h3 style="margin-bottom: 1rem;">Campos Identificados</h3>
                        <div id="mappingPreview" style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; max-height: 300px; overflow-y: auto;">
                            <!-- Items go here -->
                        </div>
                        <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                            <button onclick="window.importClient.reset()" style="background: transparent; border: 1px solid var(--text-muted); color: var(--text); padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">Cancelar</button>
                            <button onclick="window.importClient.applyMapping()" style="background: var(--success); border: none; color: white; padding: 0.5rem 1.5rem; border-radius: 6px; font-weight: bold; cursor: pointer;">Aplicar al Formulario</button>
                        </div>
                    </div>

                </div>
            </div>
            <style>
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                .drop-zone:hover { border-color: var(--primary) !important; background: rgba(59, 130, 246, 0.1); }
                .map-item { display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 0.5rem 0; font-size: 0.9rem; }
                .map-key { color: var(--text-muted); flex: 1; }
                .map-val { color: var(--primary); flex: 1; text-align: right; font-weight: 500; }
            </style>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Bind events
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');

        dropZone.onclick = () => fileInput.click();

        fileInput.onchange = (e) => {
            if (e.target.files.length > 0) this.handleFile(e.target.files[0]);
        };

        // Drag & Drop
        dropZone.ondragover = (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--primary)'; };
        dropZone.ondragleave = (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--surface-light)'; };
        dropZone.ondrop = (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--surface-light)';
            if (e.dataTransfer.files.length > 0) this.handleFile(e.dataTransfer.files[0]);
        };
    }

    async handleFile(file) {
        this.showProcessing(true);
        document.getElementById('processStatus').textContent = "Escaneando documento (OCR)...";

        const formData = new FormData();
        formData.append('file', file);

        try {
            // 1. OCR Scan
            const ocrRes = await fetch(this.ocrUrl, { method: 'POST', body: formData });
            const ocrData = await ocrRes.json();

            if (!ocrData.success) throw new Error(ocrData.error || 'Error en OCR');

            const rawText = ocrData.text;

            // 2. Map Fields
            document.getElementById('processStatus').textContent = "Analizando contenido...";
            const mapRes = await fetch(this.backendUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: rawText })
            });
            const mapData = await mapRes.json();

            if (!mapData.success) throw new Error(mapData.error || 'Error en Mapeo');

            this.currentMapping = mapData.mapped_data;
            this.showPreview(this.currentMapping);

        } catch (error) {
            alert(`Error: ${error.message}`);
            this.reset();
        }
    }

    showProcessing(show) {
        document.getElementById('uploadStep').style.display = show ? 'none' : 'block';
        document.getElementById('processingStep').style.display = show ? 'block' : 'none';
        document.getElementById('previewStep').style.display = 'none';
    }

    showPreview(data) {
        document.getElementById('processingStep').style.display = 'none';
        document.getElementById('previewStep').style.display = 'block';

        const container = document.getElementById('mappingPreview');
        container.innerHTML = '';

        if (Object.keys(data).length === 0) {
            container.innerHTML = '<p style="text-align:center; color: var(--text-muted)">No se detectaron campos conocidos.</p>';
            return;
        }

        for (const [key, val] of Object.entries(data)) {
            const div = document.createElement('div');
            div.className = 'map-item';
            div.innerHTML = `<span class="map-key">${key}</span> <span class="map-val">${val}</span>`;
            container.appendChild(div);
        }
    }

    applyMapping() {
        if (!this.currentMapping) return;

        // Check if we are on the dashboard (index.html or generic path without form)
        const isDashboard = !document.getElementById('a1_nombre_negocio'); // If the main form field doesn't exist, we are likely on the dashboard

        if (isDashboard) {
            // Check if user is trying to create a project from index
            localStorage.setItem('pending_ocr_import', JSON.stringify(this.currentMapping));
            window.location.href = 'wizard.html';
            return;
        }

        // Auto-fill logic (we are inside the wizard or a valid form)
        let count = 0;
        for (const [key, val] of Object.entries(this.currentMapping)) {
            const input = document.getElementById(key);
            if (input) {
                input.value = val;
                // Trigger change event for listeners
                input.dispatchEvent(new Event('change'));
                input.dispatchEvent(new Event('input'));
                input.classList.add('ai-filled'); // Visual feedback
                count++;
            }
        }

        alert(`✅ ${count} campos completados exitosamente.`);
        document.getElementById('importModal').style.display = 'none';

        // Notify Bob Agent UI if needed (refresh completeness)
        if (window.updateCompletenessBar) window.updateCompletenessBar();

        // Optional: trigger save if it's not a new unsaved form
        if (window.PlanIA && PlanIA.getCurrentProject() && window.triggerSave) {
            window.triggerSave();
        }

        this.reset();
    }

    checkPendingImport() {
        const pending = localStorage.getItem('pending_ocr_import');
        if (pending) {
            try {
                this.currentMapping = JSON.parse(pending);
                localStorage.removeItem('pending_ocr_import');
                console.log('📥 Found pending OCR import, applying...');
                // Wait for form to fully load
                setTimeout(() => {
                    this.applyMapping();
                }, 800);
            } catch (e) {
                console.error("Error parsing pending import", e);
            }
        }
    }

    reset() {
        this.currentMapping = null;
        document.getElementById('uploadStep').style.display = 'block';
        document.getElementById('processingStep').style.display = 'none';
        document.getElementById('previewStep').style.display = 'none';
        document.getElementById('fileInput').value = '';
    }

    open() {
        document.getElementById('importModal').style.display = 'flex';
    }
}

// Global Instance
window.importClient = new ImportClient();
document.addEventListener('DOMContentLoaded', () => window.importClient.init());
