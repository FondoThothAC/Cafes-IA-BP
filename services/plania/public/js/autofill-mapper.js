/**
 * =================================================================================
 * PROYECTO: PlanIA - Auto-Fill Mapper with AI Suggestions
 * ARCHIVO: public/js/autofill-mapper.js
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: MIT
 * DESCRIPCIÓN: Mapea datos del wizard a módulos + genera sugerencias con IA
 * =================================================================================
 */

const AutoFillMapper = {

    // AI API endpoint (Ollama)
    AI_URL: 'http://localhost:11434/api/generate',
    AI_MODEL: 'gemma3:1b',

    /**
     * Ejecuta el auto-llenado completo con sugerencias de IA
     */
    async propagateAll(projectData, useAI = true) {
        console.log('[AutoFill] Starting propagation for project:', projectData.id_proyecto);
        console.log('[AutoFill] AI enabled:', useAI);

        // Primero: mapeo directo (inmediato)
        const directMappings = {
            canvas: this.mapToCanvas(projectData),
            marketingPlan: this.mapToMarketingPlan(projectData),
            investmentBudget: this.mapToInvestmentBudget(projectData),
            revenueProjection: this.mapToRevenueProjection(projectData),
            industryAnalysis: this.mapToIndustryAnalysis(projectData)
        };

        // Guardar mapeo directo primero
        await this.saveAllMappings(projectData.id_proyecto, directMappings);

        // Segundo: si AI está habilitada, generar sugerencias
        if (useAI) {
            try {
                console.log('[AutoFill] Generating AI suggestions...');

                const aiSuggestions = await this.generateAISuggestions(projectData);

                // Merge AI suggestions with direct mappings
                if (aiSuggestions.foda) {
                    directMappings.foda = aiSuggestions.foda;
                }
                if (aiSuggestions.canvas) {
                    // Merge into existing canvas
                    Object.keys(aiSuggestions.canvas).forEach(key => {
                        if (aiSuggestions.canvas[key].length > 0) {
                            directMappings.canvas[key] = [
                                ...directMappings.canvas[key],
                                ...aiSuggestions.canvas[key]
                            ];
                        }
                    });
                }
                if (aiSuggestions.risks) {
                    directMappings.risks = aiSuggestions.risks;
                }

                // Save AI suggestions
                await this.saveAISuggestions(projectData.id_proyecto, aiSuggestions);

            } catch (error) {
                console.warn('[AutoFill] AI suggestions failed, using direct mapping only:', error);
            }
        }

        console.log('[AutoFill] Propagation complete:', directMappings);
        return directMappings;
    },

    /**
     * Genera sugerencias con IA basadas en los datos del negocio
     */
    async generateAISuggestions(data) {
        const businessContext = `
Nombre del negocio: ${data.a1_nombre_negocio || 'No especificado'}
Descripción: ${data.b1_descripcion_negocio || 'No especificado'}
Problema/Oportunidad: ${data.b2_problema_oportunidad || 'No especificado'}
Propuesta de valor: ${data.b3_propuesta_valor || 'No especificado'}
Cliente objetivo: ${data.d1_segmento_cliente || data.b4_cliente_objetivo_resumen || 'No especificado'}
Ventaja competitiva: ${data.d5_ventaja_competitiva || 'No especificado'}
Proceso de producción: ${data.e1_proceso_produccion || 'No especificado'}
        `.trim();

        const suggestions = {};

        // Generate FODA suggestions
        suggestions.foda = await this.generateFODA(businessContext);

        // Generate Canvas suggestions  
        suggestions.canvas = await this.generateCanvasSuggestions(businessContext);

        // Generate Risk suggestions
        suggestions.risks = await this.generateRiskSuggestions(businessContext);

        return suggestions;
    },

    /**
     * Genera sugerencias para FODA/SWOT
     */
    async generateFODA(context) {
        const prompt = `Eres un consultor de negocios experto. Basándote en esta información del negocio:

${context}

Genera un análisis FODA con 3 elementos por categoría. Responde SOLO en formato JSON válido, sin explicaciones adicionales:

{
  "fortalezas": ["fortaleza1", "fortaleza2", "fortaleza3"],
  "debilidades": ["debilidad1", "debilidad2", "debilidad3"],
  "oportunidades": ["oportunidad1", "oportunidad2", "oportunidad3"],
  "amenazas": ["amenaza1", "amenaza2", "amenaza3"]
}`;

        try {
            const response = await this.callAI(prompt);
            const parsed = this.parseJSONFromAI(response);

            // Convert to proper format with IDs
            const foda = {
                fortalezas: [],
                debilidades: [],
                oportunidades: [],
                amenazas: []
            };

            const timestamp = Date.now();
            ['fortalezas', 'debilidades', 'oportunidades', 'amenazas'].forEach((key, ki) => {
                if (parsed[key] && Array.isArray(parsed[key])) {
                    parsed[key].forEach((text, i) => {
                        foda[key].push({
                            id: timestamp + ki * 100 + i,
                            text: text,
                            aiSuggested: true
                        });
                    });
                }
            });

            return foda;
        } catch (error) {
            console.error('[AutoFill] FODA generation failed:', error);
            return { fortalezas: [], debilidades: [], oportunidades: [], amenazas: [] };
        }
    },

    /**
     * Genera sugerencias para Canvas
     */
    async generateCanvasSuggestions(context) {
        const prompt = `Eres un consultor de negocios experto en Business Model Canvas. Basándote en:

${context}

Genera sugerencias para completar el Canvas. Responde SOLO en formato JSON válido:

{
  "partners": ["socio clave 1", "socio clave 2"],
  "activities": ["actividad clave 1", "actividad clave 2"],
  "resources": ["recurso clave 1", "recurso clave 2"],
  "costs": ["estructura de costo 1", "estructura de costo 2"],
  "revenue": ["fuente de ingreso 1", "fuente de ingreso 2"]
}`;

        try {
            const response = await this.callAI(prompt);
            const parsed = this.parseJSONFromAI(response);

            const canvas = {
                partners: [],
                activities: [],
                resources: [],
                value: [],
                relationships: [],
                channels: [],
                segments: [],
                costs: [],
                revenue: []
            };

            const timestamp = Date.now();
            Object.keys(parsed).forEach((key, ki) => {
                if (canvas[key] !== undefined && Array.isArray(parsed[key])) {
                    parsed[key].forEach((text, i) => {
                        canvas[key].push({
                            id: timestamp + ki * 100 + i,
                            text: text,
                            aiSuggested: true
                        });
                    });
                }
            });

            return canvas;
        } catch (error) {
            console.error('[AutoFill] Canvas generation failed:', error);
            return {};
        }
    },

    /**
     * Genera sugerencias de riesgos
     */
    async generateRiskSuggestions(context) {
        const prompt = `Eres un consultor experto en análisis de riesgos. Basándote en:

${context}

Identifica los 3 principales riesgos y planes de mitigación. Responde SOLO en JSON:

{
  "risks": [
    {"tipo": "mercado", "riesgo": "descripción", "mitigacion": "plan de mitigación"},
    {"tipo": "operativo", "riesgo": "descripción", "mitigacion": "plan de mitigación"},
    {"tipo": "financiero", "riesgo": "descripción", "mitigacion": "plan de mitigación"}
  ]
}`;

        try {
            const response = await this.callAI(prompt);
            const parsed = this.parseJSONFromAI(response);
            return parsed.risks || [];
        } catch (error) {
            console.error('[AutoFill] Risk generation failed:', error);
            return [];
        }
    },

    /**
     * Llama a la API de Ollama
     */
    async callAI(prompt) {
        const response = await fetch(this.AI_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: this.AI_MODEL,
                prompt: prompt,
                stream: false,
                options: {
                    temperature: 0.7,
                    num_predict: 500
                }
            })
        });

        if (!response.ok) {
            throw new Error(`AI API error: ${response.status}`);
        }

        const data = await response.json();
        return data.response || '';
    },

    /**
     * Extrae JSON de respuesta de IA
     */
    parseJSONFromAI(text) {
        // Find JSON in response
        const jsonMatch = text.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            return JSON.parse(jsonMatch[0]);
        }
        throw new Error('No JSON found in AI response');
    },

    // ==================== DIRECT MAPPING FUNCTIONS ====================

    /**
     * Canvas (Business Model Canvas) - Direct mapping
     */
    mapToCanvas(data) {
        const canvas = {
            partners: [],
            activities: [],
            resources: [],
            value: [],
            relationships: [],
            channels: [],
            segments: [],
            costs: [],
            revenue: []
        };

        // Propuesta de valor → Value block
        if (data.b3_propuesta_valor) {
            canvas.value.push({
                id: Date.now(),
                text: data.b3_propuesta_valor.substring(0, 200)
            });
        }

        // Segmento cliente → Segments block
        if (data.d1_segmento_cliente) {
            canvas.segments.push({
                id: Date.now() + 1,
                text: data.d1_segmento_cliente.substring(0, 200)
            });
        }

        // Cliente objetivo → Segments block
        if (data.b4_cliente_objetivo_resumen) {
            canvas.segments.push({
                id: Date.now() + 2,
                text: `Cliente objetivo: ${data.b4_cliente_objetivo_resumen}`
            });
        }

        // Canales de venta → Channels block
        if (data.f3_canales_venta) {
            data.f3_canales_venta.split(',').forEach((canal, i) => {
                canvas.channels.push({
                    id: Date.now() + 10 + i,
                    text: canal.trim()
                });
            });
        }

        // Proceso producción → Activities block
        if (data.e1_proceso_produccion) {
            canvas.activities.push({
                id: Date.now() + 20,
                text: data.e1_proceso_produccion.substring(0, 200)
            });
        }

        // Estrategia promoción → Relationships block
        if (data.f4_estrategia_promocion) {
            canvas.relationships.push({
                id: Date.now() + 30,
                text: data.f4_estrategia_promocion.substring(0, 200)
            });
        }

        return canvas;
    },

    /**
     * FODA (SWOT Analysis) - Direct mapping (kept for compatibility, but AI will override/enhance)
     */
    mapToFoda(data) {
        const foda = {
            fortalezas: [],
            debilidades: [],
            oportunidades: [],
            amenazas: []
        };

        // Experiencia → Fortaleza
        if (data.c1_experiencia_habilidades) {
            foda.fortalezas.push({
                id: Date.now(),
                text: `Experiencia: ${data.c1_experiencia_habilidades.substring(0, 100)}`
            });
        }

        // Ventaja competitiva → Fortaleza
        if (data.d5_ventaja_competitiva) {
            foda.fortalezas.push({
                id: Date.now() + 1,
                text: data.d5_ventaja_competitiva.substring(0, 150)
            });
        }

        // Problema/Oportunidad → Oportunidad
        if (data.b2_problema_oportunidad) {
            foda.oportunidades.push({
                id: Date.now() + 10,
                text: data.b2_problema_oportunidad.substring(0, 150)
            });
        }

        return foda;
    },

    /**
     * Marketing Plan - Direct mapping
     */
    mapToMarketingPlan(data) {
        const marketing = {};

        // Estrategia de precios
        if (data.f2_estrategia_precios) {
            marketing.h4_justificacion_precio = data.f2_estrategia_precios;
        }

        // Precio promedio
        if (data.g5_precio_promedio) {
            marketing.h2_precio_promedio = data.g5_precio_promedio;
        }

        // Canales
        if (data.f3_canales_venta) {
            const canales = data.f3_canales_venta.toLowerCase();
            const channelMap = [];
            if (canales.includes('whatsapp')) channelMap.push('whatsapp');
            if (canales.includes('redes') || canales.includes('facebook') || canales.includes('instagram')) channelMap.push('redes_sociales');
            if (canales.includes('local') || canales.includes('físic') || canales.includes('tienda')) channelMap.push('tienda_fisica');
            if (canales.includes('online') || canales.includes('ecommerce') || canales.includes('web')) channelMap.push('ecommerce');
            marketing.h5_canales_distribucion = channelMap.join(',');
        }

        // Funnel data
        if (data.i_mercado_objetivo) {
            marketing.h10_funnel_awareness = data.i_mercado_objetivo;
        }
        if (data.i_alcance_pct && data.i_mercado_objetivo) {
            marketing.h11_funnel_consideracion = Math.round(data.i_mercado_objetivo * (data.i_alcance_pct / 100));
        }
        if (data.i_conversion_pct && data.i_mercado_objetivo && data.i_alcance_pct) {
            const consideracion = data.i_mercado_objetivo * (data.i_alcance_pct / 100);
            marketing.h13_funnel_compra = Math.round(consideracion * (data.i_conversion_pct / 100));
        }

        return marketing;
    },

    /**
     * Investment Budget - Direct mapping
     */
    mapToInvestmentBudget(data) {
        const investment = [];

        // Inversión inicial como concepto general
        if (data.g8_inversion_inicial) {
            investment.push({
                concepto: 'Capital inicial general',
                tipo: 'Capital',
                cantidad: 1,
                costoUnitario: parseFloat(data.g8_inversion_inicial),
                programa: parseFloat(data.b5_monto_solicitado) || 0,
                socios: parseFloat(data.g8_inversion_inicial) - (parseFloat(data.b5_monto_solicitado) || 0)
            });
        }

        return investment;
    },

    /**
     * Revenue Projection - from BOM products
     */
    mapToRevenueProjection(data) {
        const products = [];

        // Parse BOM from wizard if exists
        try {
            const bom = JSON.parse(data.e3_bom_productos_json || '[]');
            bom.forEach((item, i) => {
                products.push({
                    nombre: item.nombre || `Producto ${i + 1}`,
                    precio: parseFloat(item.precio) || 0,
                    costo: parseFloat(item.costo) || 0,
                    unidadesMes: parseInt(item.cantidad) || 10
                });
            });
        } catch (e) {
            // If no BOM, create default from precio promedio
            if (data.g5_precio_promedio) {
                products.push({
                    nombre: 'Producto/Servicio Principal',
                    precio: parseFloat(data.g5_precio_promedio),
                    costo: parseFloat(data.g5_precio_promedio) * 0.6, // Assume 40% margin
                    unidadesMes: 50
                });
            }
        }

        return { productos: products, crecimiento: 10 };
    },

    /**
     * Industry Analysis - Direct mapping
     */
    mapToIndustryAnalysis(data) {
        const industry = {};

        // TAM/SAM/SOM from funnel
        if (data.i_mercado_objetivo && data.g5_precio_promedio) {
            const precio = parseFloat(data.g5_precio_promedio);
            const mercado = parseInt(data.i_mercado_objetivo);
            industry.ind_tam_num = mercado * precio * 12; // Annual TAM

            if (data.i_alcance_pct) {
                industry.ind_sam_num = industry.ind_tam_num * (data.i_alcance_pct / 100);
            }
            if (data.i_conversion_pct && data.i_alcance_pct) {
                industry.ind_som_num = industry.ind_sam_num * (data.i_conversion_pct / 100);
            }
        }

        return industry;
    },

    // ==================== SAVE FUNCTIONS ====================

    /**
     * Save direct mappings to database
     */
    async saveAllMappings(projectId, mappings) {
        const updates = {
            id_proyecto: projectId,
            action: 'update'
        };

        // Canvas → JSON field
        if (Object.values(mappings.canvas).some(arr => arr.length > 0)) {
            updates.c2_canvas_json = JSON.stringify(mappings.canvas);
        }

        // FODA → JSON field (only if direct mapping has data, AI will handle its own save)
        if (mappings.foda && Object.values(mappings.foda).some(arr => arr.length > 0)) {
            updates.c3_foda_json = JSON.stringify(mappings.foda);
        }

        // Marketing Plan → individual fields
        Object.assign(updates, mappings.marketingPlan);

        // Investment Budget → JSON field
        if (mappings.investmentBudget.length > 0) {
            updates.g10_presupuesto_inversion_json = JSON.stringify(mappings.investmentBudget);
        }

        // Revenue Projection → JSON field
        if (mappings.revenueProjection.productos.length > 0) {
            updates.g12_proyeccion_ingresos_json = JSON.stringify(mappings.revenueProjection);
        }

        // Industry Analysis → individual fields
        Object.assign(updates, mappings.industryAnalysis);

        try {
            const response = await fetch('save_row.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });
            const result = await response.json();
            console.log('[AutoFill] Direct mappings save result:', result);
            return result;
        } catch (error) {
            console.error('[AutoFill] Direct mappings save error:', error);
            throw error;
        }
    },

    /**
     * Save AI suggestions to database
     */
    async saveAISuggestions(projectId, suggestions) {
        const updates = {
            id_proyecto: projectId,
            action: 'update'
        };

        if (suggestions.foda && Object.values(suggestions.foda).some(arr => arr.length > 0)) {
            updates.c3_foda_json = JSON.stringify(suggestions.foda);
        }

        // If canvas suggestions are generated, they are merged into the directMappings.canvas
        // and saved with saveAllMappings. No separate save needed here.

        if (suggestions.risks && suggestions.risks.length > 0) {
            updates.c4_riesgos_json = JSON.stringify(suggestions.risks);
        }

        try {
            const response = await fetch('save_row.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });
            const result = await response.json();
            console.log('[AutoFill] AI suggestions save result:', result);
            return result;
        } catch (error) {
            console.error('[AutoFill] AI suggestions save error:', error);
            throw error;
        }
    }
};

// Export for use
window.AutoFillMapper = AutoFillMapper;
