/**
 * Cliente JS para interactuar con el Agente Bob (Python API)
 */
class BobAgentClient {
    constructor(apiUrl = null) {
        // Detectar host dinámicamente para soportar acceso remoto
        const host = window.location.hostname;
        const gatewayPort = 3002;
        this.apiUrl = apiUrl || `http://${host}:${gatewayPort}/api/agent`;
        this.isLoading = false;
    }

    async runAnalysis(projectId) {
        if (this.isLoading) return;
        this.isLoading = true;
        this.showLoadingModal();

        try {
            console.log(`🤖 Solicitando análisis a Bob para proyecto ${projectId}...`);
            const response = await fetch(`${this.apiUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ project_id: projectId })
            });

            if (!response.ok) {
                throw new Error(`Error del servidor: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                this.showResultsModal(data);
            } else {
                alert(`Error: ${data.error}`);
            }

        } catch (error) {
            console.error(error);
            alert(`No se pudo conectar con el Agente Bob: ${error.message}`);
        } finally {
            this.isLoading = false;
            this.hideLoadingModal();
        }
    }

    showLoadingModal() {
        // Simple loading overlay
        let modal = document.getElementById('bob-loading-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'bob-loading-modal';
            modal.innerHTML = `
                <div style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:9999;display:flex;justify-content:center;align-items:center;flex-direction:column;color:white;">
                    <div style="font-size:40px;margin-bottom:20px;">🤖</div>
                    <h2>Bob está analizando tu proyecto...</h2>
                    <p>Consultando metodologías, precios y competidores.</p>
                </div>
            `;
            document.body.appendChild(modal);
        }
        modal.style.display = 'flex';
    }

    hideLoadingModal() {
        const modal = document.getElementById('bob-loading-modal');
        if (modal) modal.style.display = 'none';
    }

    showResultsModal(data) {
        // Results modal
        const { analysis, suggestions } = data;
        let html = `
            <div style="background:var(--surface, #1e293b);padding:30px;border-radius:12px;max-width:800px;width:90%;max-height:90vh;overflow-y:auto;position:relative;color:var(--text, #fff);">
                <button onclick="document.getElementById('bob-results-modal').remove()" style="position:absolute;top:15px;right:15px;background:none;border:none;color:white;font-size:20px;cursor:pointer;">&times;</button>
                
                <h2 style="color:#60a5fa;margin-bottom:10px;">🤖 Análisis de Bob Finalizado</h2>
                
                <div style="display:flex;gap:15px;margin-bottom:20px;background:rgba(255,255,255,0.05);padding:15px;border-radius:8px;">
                    <div><strong>Industria:</strong> ${analysis.industry}</div>
                    <div><strong>Complejidad:</strong> ${analysis.complexity}</div>
                </div>

                <h3>💡 Sugerencias Encontradas (${Object.keys(suggestions).length} módulos)</h3>
        `;

        for (const [module, fields] of Object.entries(suggestions)) {
            html += `<div style="margin-bottom:15px;">
                        <h4 style="text-transform:capitalize;color:#fbbf24;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:5px;">${module}</h4>
                        <ul style="list-style:none;padding-left:0;">`;

            for (const [field, value] of Object.entries(fields)) {
                // Truncate long values for display
                const displayValue = typeof value === 'string' && value.length > 100
                    ? value.substring(0, 100) + '...'
                    : value;

                html += `<li style="margin-bottom:8px;font-size:0.9rem;">
                            <span style="color:#94a3b8;font-family:monospace;">${field}:</span> 
                            <span style="color:#e2e8f0;">${displayValue}</span>
                            <button onclick="applySuggestion('${field}', '${btoa(unescape(encodeURIComponent(JSON.stringify(value))))}')" 
                                    style="margin-left:10px;padding:2px 8px;background:#22c55e;border:none;border-radius:4px;color:white;cursor:pointer;font-size:0.8rem;">
                                Aplicar
                            </button>
                         </li>`;
            }
            html += `</ul></div>`;
        }

        html += `
            <div style="margin-top:20px;text-align:right;">
                <button onclick="document.getElementById('bob-results-modal').remove()" style="padding:10px 20px;background:#3b82f6;color:white;border:none;border-radius:6px;cursor:pointer;">Cerrar</button>
            </div>
        </div>`;

        let modal = document.createElement('div');
        modal.id = 'bob-results-modal';
        modal.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:9998;display:flex;justify-content:center;align-items:center;";
        modal.innerHTML = html;
        document.body.appendChild(modal);
    }
}

// Global helper to apply suggestions
window.applySuggestion = function (fieldId, encodedValue) {
    try {
        const value = JSON.parse(decodeURIComponent(escape(atob(encodedValue))));
        const input = document.getElementById(fieldId) || document.querySelector(`[name="${fieldId}"]`);

        if (input) {
            input.value = typeof value === 'object' ? JSON.stringify(value) : value;
            // Trigger change event for listeners
            input.dispatchEvent(new Event('change'));
            input.style.border = "2px solid #22c55e"; // Highlight success
            setTimeout(() => input.style.border = "", 2000);
        } else {
            alert(`Campo ${fieldId} no encontrado en el formulario.`);
        }
    } catch (e) {
        console.error("Error aplicando sugerencia:", e);
    }
};

// Initialize client
const bobClient = new BobAgentClient();
window.runBobAgentGlobal = () => {
    // Get project ID from select or state
    // For now assuming existing global state or hardcoded for demo
    // PlanIA.state.currentProject
    let projectId = 1;
    if (typeof PlanIA !== 'undefined' && PlanIA.state && PlanIA.state.currentProject) {
        projectId = PlanIA.state.currentProject;
    } else {
        // Fallback: try to get from local storage
        projectId = localStorage.getItem('plania_current_project') || 1;
    }

    bobClient.runAnalysis(projectId);
};
