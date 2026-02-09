/**
 * =================================================================================
 * PROYECTO: PlanIA - AI Brand Search
 * ARCHIVO: public/js/brand-search.js
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: MIT
 * DESCRIPCIÓN: Búsqueda inteligente de marca usando IA para encontrar redes sociales
 * =================================================================================
 */

const BrandSearch = {

    // AI API endpoint - Uses api-gateway for remote access compatibility
    AI_URL: `http://${window.location.hostname}:3002/api/generate`,
    AI_MODEL: 'gemma3:1b',

    /**
     * Busca información de marca usando IA
     */
    async search(brandName, businessDescription = '') {
        console.log('[BrandSearch] Searching for:', brandName);

        const resultsContainer = document.getElementById('search-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = '<div class="search-loading">🔄 Buscando información de marca...</div>';
        }

        try {
            const results = await this.inferBrandInfo(brandName, businessDescription);
            this.renderResults(results);
            return results;
        } catch (error) {
            console.error('[BrandSearch] Error:', error);
            if (resultsContainer) {
                resultsContainer.innerHTML = '<div class="search-error">⚠️ No se pudo conectar con IA. Verifica que Ollama esté corriendo.</div>';
            }
            return null;
        }
    },

    /**
     * Usa IA para inferir información de la marca
     */
    async inferBrandInfo(brandName, description) {
        const prompt = `Eres un experto en marketing digital y branding. Dado el nombre de una empresa o emprendimiento, infiere la información más probable.

Nombre del negocio: "${brandName}"
${description ? `Descripción: "${description}"` : ''}

Genera información probable sobre esta marca en formato JSON. Incluye posibles URLs de redes sociales basándote en patrones comunes (nombre sin espacios, con guiones, etc).

Responde SOLO con JSON válido, sin explicaciones:

{
  "suggestions": [
    {
      "name": "Nombre sugerido",
      "domain": "ejemplo.com",
      "facebook": "https://facebook.com/ejemplo",
      "instagram": "https://instagram.com/ejemplo",
      "tiktok": "https://tiktok.com/@ejemplo",
      "website": "https://ejemplo.com",
      "slogan_suggestion": "Eslogan sugerido basado en el tipo de negocio",
      "colors_suggestion": ["#color1", "#color2", "#color3"],
      "confidence": "high/medium/low"
    }
  ],
  "industry": "Industria detectada",
  "tips": ["Consejo 1 para la marca", "Consejo 2"]
}`;

        const response = await fetch(this.AI_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: this.AI_MODEL,
                prompt: prompt,
                stream: false,
                options: {
                    temperature: 0.7,
                    num_predict: 800
                }
            })
        });

        if (!response.ok) {
            throw new Error(`AI API error: ${response.status}`);
        }

        const data = await response.json();
        const aiResponse = data.response || '';

        // Parse JSON from AI response
        const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            const parsed = JSON.parse(jsonMatch[0]);
            parsed.brandName = brandName;
            return parsed;
        }

        throw new Error('No valid JSON in AI response');
    },

    /**
     * Renderiza los resultados de búsqueda
     */
    renderResults(results) {
        const container = document.getElementById('search-results');
        if (!container || !results) return;

        let html = `
            <div class="search-results-header">
                <h4>🔍 Resultados para "${results.brandName}"</h4>
                <p class="industry-tag">📁 Industria: ${results.industry || 'General'}</p>
            </div>
        `;

        if (results.suggestions && results.suggestions.length > 0) {
            html += '<div class="brand-suggestions">';

            results.suggestions.forEach((suggestion, index) => {
                const logoUrl = suggestion.domain
                    ? `https://logo.clearbit.com/${suggestion.domain}`
                    : null;

                html += `
                    <div class="brand-result-card" data-index="${index}">
                        <div class="result-logo-container">
                            ${logoUrl
                        ? `<img src="${logoUrl}" class="result-logo" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                   <div class="logo-placeholder" style="display:none;">🏢</div>`
                        : '<div class="logo-placeholder">🏢</div>'
                    }
                        </div>
                        <div class="result-info">
                            <h4>${suggestion.name || results.brandName}</h4>
                            ${suggestion.slogan_suggestion ? `<p class="suggested-slogan">"${suggestion.slogan_suggestion}"</p>` : ''}
                            <div class="social-links-preview">
                                ${suggestion.facebook ? `<a href="${suggestion.facebook}" target="_blank" class="social-link fb">📘 FB</a>` : ''}
                                ${suggestion.instagram ? `<a href="${suggestion.instagram}" target="_blank" class="social-link ig">📸 IG</a>` : ''}
                                ${suggestion.tiktok ? `<a href="${suggestion.tiktok}" target="_blank" class="social-link tt">🎵 TT</a>` : ''}
                                ${suggestion.website ? `<a href="${suggestion.website}" target="_blank" class="social-link web">🌐 Web</a>` : ''}
                            </div>
                            ${suggestion.colors_suggestion ? `
                                <div class="color-preview">
                                    ${suggestion.colors_suggestion.map(c => `<span class="color-dot" style="background:${c}"></span>`).join('')}
                                </div>
                            ` : ''}
                        </div>
                        <div class="result-actions">
                            <span class="confidence-badge ${suggestion.confidence}">${suggestion.confidence || 'medium'}</span>
                            <button class="btn-select-brand" onclick="BrandSearch.selectSuggestion(${index})">
                                ✓ Usar esta
                            </button>
                        </div>
                    </div>
                `;
            });

            html += '</div>';
        }

        if (results.tips && results.tips.length > 0) {
            html += `
                <div class="brand-tips">
                    <h5>💡 Consejos de IA:</h5>
                    <ul>
                        ${results.tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        container.innerHTML = html;

        // Store results for selection
        this.lastResults = results;
    },

    /**
     * Aplica la sugerencia seleccionada a los campos del formulario
     */
    selectSuggestion(index) {
        if (!this.lastResults || !this.lastResults.suggestions) return;

        const suggestion = this.lastResults.suggestions[index];
        if (!suggestion) return;

        console.log('[BrandSearch] Applying suggestion:', suggestion);

        // Fill form fields
        const mappings = {
            'brand_name': suggestion.name || this.lastResults.brandName,
            'brand_slogan': suggestion.slogan_suggestion || '',
            'social_facebook': suggestion.facebook || '',
            'social_instagram': suggestion.instagram || '',
            'social_tiktok': suggestion.tiktok || '',
            'social_website': suggestion.website || ''
        };

        Object.entries(mappings).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el && value) {
                el.value = value;
                el.dispatchEvent(new Event('change'));
            }
        });

        // Apply colors if available
        if (suggestion.colors_suggestion && suggestion.colors_suggestion.length >= 3) {
            const colorIds = ['color_primary', 'color_secondary', 'color_accent'];
            suggestion.colors_suggestion.slice(0, 3).forEach((color, i) => {
                const colorPicker = document.getElementById(colorIds[i]);
                if (colorPicker) {
                    colorPicker.value = color;
                    colorPicker.dispatchEvent(new Event('input'));
                }
            });
        }

        // Visual feedback
        const selectedCard = document.querySelector(`.brand-result-card[data-index="${index}"]`);
        document.querySelectorAll('.brand-result-card').forEach(c => c.classList.remove('selected'));
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }

        // Show success message
        const container = document.getElementById('search-results');
        if (container) {
            const successMsg = document.createElement('div');
            successMsg.className = 'selection-success';
            successMsg.innerHTML = '✅ Datos aplicados. Puedes editarlos en los campos de arriba.';
            container.appendChild(successMsg);
        }
    }
};

// Export
window.BrandSearch = BrandSearch;
