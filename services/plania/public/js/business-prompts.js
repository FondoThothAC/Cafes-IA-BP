/**
 * =================================================================================
 * PROYECTO: PlanIA - Business Framework Prompts
 * ARCHIVO: public/js/business-prompts.js
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: MIT
 * DESCRIPCIÓN: Prompts basados en frameworks de negocios académicos
 *              (Harvard, MIT, Stanford, Osterwalder, Porter, Maurya)
 * =================================================================================
 */

const BusinessPrompts = {

    /**
     * Obtiene todos los datos relevantes del wizard
     */
    getWizardContext() {
        const getValue = (id) => document.getElementById(id)?.value || '';

        return {
            // Datos básicos
            businessName: getValue('a1_nombre_negocio') || 'el negocio',
            entrepreneur: getValue('a2_nombre_emprendedor') || 'el emprendedor',
            presentation: getValue('a4_carta_presentacion'),

            // Descripción
            description: getValue('b1_descripcion_negocio'),
            problem: getValue('b2_problema_oportunidad'),
            valueProposition: getValue('b3_propuesta_valor'),
            targetClient: getValue('b4_cliente_objetivo_resumen'),
            requestedAmount: getValue('b5_monto_solicitado'),

            // Emprendedor
            experience: getValue('c1_experiencia_habilidades'),
            motivation: getValue('c2_motivacion'),
            timeCommitment: getValue('c3_compromiso_tiempo'),

            // Mercado
            segment: getValue('d1_segmento_cliente'),
            competitiveAdvantage: getValue('d5_ventaja_competitiva'),
            location: getValue('d8_direccion_formateada') || 'ubicación no especificada',
            latitude: getValue('d6_latitud'),
            longitude: getValue('d7_longitud'),

            // Operaciones
            productionProcess: getValue('e1_proceso_produccion'),
            productionCapacity: getValue('e2_capacidad_produccion'),

            // Marketing
            brandName: getValue('f1_nombre_marca'),
            pricingStrategy: getValue('f2_estrategia_precios'),
            salesChannels: getValue('f3_canales_venta'),
            promotionStrategy: getValue('f4_estrategia_promocion'),
            averagePrice: getValue('g5_precio_promedio'),

            // Finanzas
            fixedCosts: getValue('g5_costos_fijos_mensuales'),
            initialInvestment: getValue('g8_inversion_inicial'),
            capitalUse: getValue('g9_uso_capital'),

            // Impacto
            socialImpact: getValue('h1_impacto_social'),
            economicImpact: getValue('h2_impacto_economico'),
            commitment: getValue('h4_compromiso')
        };
    },

    /**
     * Genera el prompt para un campo específico usando frameworks de negocios
     */
    getPrompt(fieldId) {
        const ctx = this.getWizardContext();

        // Contexto común para todos los prompts
        const commonContext = `
CONTEXTO DEL NEGOCIO:
- Nombre: ${ctx.businessName}
- Descripción: ${ctx.description || 'No especificada'}
- Segmento objetivo: ${ctx.segment || 'No especificado'}
- Ubicación: ${ctx.location}
- Propuesta de valor actual: ${ctx.valueProposition || 'No definida'}
`;

        const prompts = {
            // ═══════════════════════════════════════════════════════════════
            // UNIDAD I: PORTADA - Identidad básica
            // ═══════════════════════════════════════════════════════════════

            'nombre_negocio': `Eres experto en naming y branding (metodología de Interbrand).
            
Sugiere 3 nombres para un negocio con estos criterios:
- Descripción: ${ctx.description || 'nuevo emprendimiento'}
- Sector: inferir del contexto

CRITERIOS DE EVALUACIÓN (Interbrand):
1. Diferenciación - único en el mercado
2. Relevancia - conecta con el público objetivo
3. Coherencia - refleja la esencia del negocio
4. Pronunciabilidad - fácil de decir y recordar
5. Disponibilidad - potencial de dominio web

Responde con 3 nombres, formato:
* [NOMBRE] - [Razón en 10 palabras max]`,

            'carta_presentacion': `Eres experto en comunicación empresarial (Harvard Business Review).
${commonContext}

Redacta una Carta de Presentación usando estructura AIDA:
A - Atención: Hook inicial impactante
I - Interés: Problema que resolvemos  
D - Deseo: Nuestra solución única
A - Acción: Llamado a colaborar

Máximo 5 oraciones. Tono: profesional pero cercano.`,

            // ═══════════════════════════════════════════════════════════════
            // UNIDAD II: RESUMEN EJECUTIVO - Estructura del negocio
            // ═══════════════════════════════════════════════════════════════

            'descripcion_negocio': `Eres consultor de startups (Y Combinator style).
${commonContext}

Redacta una descripción ejecutiva usando el formato "Elevator Pitch" de 30 segundos:

"[Negocio] ayuda a [segmento específico] a [resolver problema] mediante [solución única], a diferencia de [alternativas] que [limitación]."

Máximo 3 oraciones claras. Evita jerga técnica.`,

            'problema_oportunidad': `Eres analista de mercado usando el framework "Jobs To Be Done" (Clayton Christensen, Harvard).
${commonContext}

Identifica el problema/oportunidad usando JTBD:
1. JOB FUNCIONAL: ¿Qué tarea práctica quiere completar el cliente?
2. JOB EMOCIONAL: ¿Cómo quiere sentirse?
3. JOB SOCIAL: ¿Cómo quiere ser percibido?

Y la OPORTUNIDAD:
- ¿Por qué las soluciones actuales no satisfacen estos jobs?
- ¿Cuál es el gap de mercado?

Formato estructurado, máximo 5 líneas.`,

            'propuesta_valor': `Eres estratega usando el Value Proposition Canvas (Alexander Osterwalder).
${commonContext}

Genera una Propuesta de Valor usando la fórmula:

"Para [SEGMENTO con característica específica]
que [NECESIDAD/FRUSTRACIÓN principal],
[NEGOCIO] es [CATEGORÍA]
que [BENEFICIO CLAVE].
A diferencia de [ALTERNATIVA],
nosotros [DIFERENCIADOR ÚNICO]."

Sé específico con datos cuando sea posible.`,

            'cliente_objetivo': `Eres experto en segmentación usando el modelo STP (Kotler, MIT Sloan).
${commonContext}

Define el Cliente Objetivo con estos elementos:

DEMOGRAFÍA:
- Edad, género, ubicación, NSE

PSICOGRAFÍA:
- Intereses, valores, estilo de vida

COMPORTAMIENTO:
- Frecuencia de compra, canales preferidos
- Triggers de compra
- Objeciones comunes

NECESIDAD PRINCIPAL que resuelve el negocio.

Formato bullet points, específico y accionable.`,

            // ═══════════════════════════════════════════════════════════════
            // UNIDAD III: EMPRENDEDOR - Perfil y motivación
            // ═══════════════════════════════════════════════════════════════

            'experiencia': `Eres coach de emprendedores (Stanford d.school approach).
${commonContext}
Emprendedor: ${ctx.entrepreneur}

Sugiere cómo presentar la experiencia relevante para operar este negocio.
Incluye:
- Habilidades técnicas transferibles
- Experiencia en industrias similares
- Logros cuantificables
- Formación relevante

Redacta en primera persona, 3-4 oraciones.`,

            'motivacion': `Eres mentor de startups (siguiendo el modelo de "Start With Why" - Simon Sinek).
${commonContext}

Articula la motivación del emprendedor usando el Círculo Dorado:
WHY - ¿Por qué existimos? (propósito profundo)
HOW - ¿Cómo lo hacemos diferente?
WHAT - ¿Qué hacemos concretamente?

Redacta en primera persona, auténtico y emotivo, 3 oraciones.`,

            // ═══════════════════════════════════════════════════════════════
            // UNIDAD IV: MERCADO - Análisis competitivo
            // ═══════════════════════════════════════════════════════════════

            'segmento_cliente': `Eres analista de mercado usando TAM-SAM-SOM (metodología VC estándar).
${commonContext}

Define el segmento de mercado:

TAM (Total Addressable Market):
- Mercado total de la industria

SAM (Serviceable Available Market):  
- Porción que puedes alcanzar geográficamente

SOM (Serviceable Obtainable Market):
- Meta realista año 1

Incluye números estimados cuando sea posible.`,

            'ventaja_competitiva': `Eres estratega usando las 5 Fuerzas de Porter (Harvard Business School).
${commonContext}

Analiza la posición competitiva:

1. RIVALIDAD EXISTENTE: ¿Quiénes compiten hoy?
2. AMENAZA DE NUEVOS: ¿Barreras de entrada?
3. PODER DE PROVEEDORES: ¿Dependencia?
4. PODER DE CLIENTES: ¿Alternativas que tienen?
5. SUSTITUTOS: ¿Qué más resuelve el problema?

Y 3 VENTAJAS COMPETITIVAS del negocio vs estas fuerzas.`,

            // ═══════════════════════════════════════════════════════════════
            // UNIDAD V: OPERACIONES - Procesos
            // ═══════════════════════════════════════════════════════════════

            'proceso_produccion': `Eres ingeniero industrial usando LEAN Manufacturing.
${commonContext}

Describe el proceso de operación usando:

FLUJO DE VALOR:
1. INPUT: ¿Qué insumos/recursos?
2. PROCESO: Pasos de transformación
3. OUTPUT: ¿Qué entregamos al cliente?

TIEMPOS:
- Lead time estimado
- Cuellos de botella potenciales

Máximo 5 pasos numerados.`,

            // ═══════════════════════════════════════════════════════════════
            // UNIDAD VI: MARKETING - Estrategia comercial
            // ═══════════════════════════════════════════════════════════════

            'marca': `Eres experto en branding (metodología de Marty Neumeier, "The Brand Gap").
${commonContext}

Sugiere elementos de identidad de marca:

ESENCIA DE MARCA:
- Personalidad (5 adjetivos)
- Tono de voz

ELEMENTOS VISUALES:
- Colores recomendados (con hex y razón)
- Estilo tipográfico

ESLOGAN:
- 3 opciones (máximo 6 palabras cada uno)`,

            'estrategia_precios': `Eres consultor de pricing usando estrategias de MIT Sloan.
${commonContext}
Precio promedio actual: ${ctx.averagePrice || 'No definido'}

Define estrategia de precios:

TIPO DE ESTRATEGIA:
- Penetración / Premium / Competitiva / Valor

ESTRUCTURA DE PRECIOS:
- Precio base sugerido
- Opciones de upsell

JUSTIFICACIÓN:
- Por qué este nivel de precio
- Comparación con alternativas

Datos específicos cuando sea posible.`,

            'promocion': `Eres growth marketer usando el modelo AARRR (Pirate Metrics - Dave McClure).
${commonContext}
Segmento: ${ctx.segment || 'No definido'}

Sugiere estrategia de promoción para cada etapa:

ACQUISITION: ¿Cómo atraer visitantes?
- 2 canales específicos

ACTIVATION: ¿Cómo dar buena primera experiencia?
- 1 táctica

RETENTION: ¿Cómo hacer que vuelvan?
- 1 táctica

REVENUE: ¿Cómo monetizar?
- 1 táctica

REFERRAL: ¿Cómo generar recomendaciones?
- 1 táctica

Acciones de bajo costo, alta efectividad.`,

            // ═══════════════════════════════════════════════════════════════
            // UNIDAD VII: FINANZAS - Estructura financiera
            // ═══════════════════════════════════════════════════════════════

            'uso_capital': `Eres CFO usando mejores prácticas de capital allocation.
${commonContext}
Monto solicitado: ${ctx.requestedAmount || 'No especificado'}
Inversión inicial: ${ctx.initialInvestment || 'No especificada'}

Describe el uso del capital con estructura:

DISTRIBUCIÓN SUGERIDA:
- % Equipo/Infraestructura
- % Inventario inicial  
- % Marketing/Lanzamiento
- % Capital de trabajo
- % Reserva de contingencia

PRIORIDADES:
- Top 3 gastos críticos para iniciar

Incluye montos estimados si hay datos.`,

            // ═══════════════════════════════════════════════════════════════
            // UNIDAD VIII: IMPACTO - Contribución social y económica
            // ═══════════════════════════════════════════════════════════════

            'impacto_social': `Eres experto en impacto social usando los ODS (Objetivos de Desarrollo Sostenible, ONU).
${commonContext}
Ubicación: ${ctx.location}

Describe el impacto social:

ODS RELACIONADOS:
- ¿Qué objetivos contribuye a alcanzar?

IMPACTO DIRECTO:
- Empleos generados (directos e indirectos)
- Beneficiarios de la comunidad

VALOR SOCIAL:
- ¿Qué cambia en la vida de las personas?

Sé específico con números cuando posible.`,

            'impacto_economico': `Eres economista analizando impacto empresarial local.
${commonContext}
Ubicación: ${ctx.location}

Describe el impacto económico:

CONTRIBUCIÓN FISCAL:
- Estimación de impuestos generados

CADENA DE VALOR LOCAL:
- Proveedores locales beneficiados
- Sectores económicos impactados

MULTIPLICADOR ECONÓMICO:
- Circulación de dinero en la comunidad

Incluye estimaciones numéricas realistas.`,

            // ═══════════════════════════════════════════════════════════════
            // UNIDAD IX: ESTRATEGIA AVANZADA (MBA Modules)
            // ═══════════════════════════════════════════════════════════════

            'pestel_analisis': `Eres estratega corporativo experto en leyes y economía de México.
${commonContext}
Ubicación: ${ctx.location}

INVESTIGACIÓN EN TIEMPO REAL REQUERIDA (Fuentes Oficiales):
Por favor, busca y analiza información reciente de:
- DOF (Diario Oficial de la Federación): Nuevas NOMs, reformas laborales o fiscales vigentes.
- Banxico/INEGI: Tasa de inflación actual, TIIE, crecimiento PIB sectorial.
- Noticias: Cambios políticos recientes que afecten al sector.

Con esa data, construye el PESTEL identificando Oportunidades (O) y Amenazas (A):

P - POLÍTICO: (Ej: Reformas recientes, estabilidad, clima de inversión)
E - ECONÓMICO: (Ej: Inflación, tipo de cambio, tasas de interés)
S - SOCIAL: (Ej: Cambios demográficos, nuevos hábitos de consumo)
T - TECNOLÓGICO: (Ej: Adopción tecnológica, automatización)
E - ECOLÓGICO: (Ej: Regulaciones ambientales, escasez de agua)
L - LEGAL: (Ej: Reformas a Ley Federal del Trabajo, impuestos digitales)

Cita la fuente cuando sea posible (ej: "Según Banxico...").`,

            'tows_matrix': `Eres consultor de estrategia usando la Matriz TOWS (Heinz Weihrich).
${commonContext}
Propuesta de Valor: ${ctx.valueProposition}

Genera ESTRATEGIAS DE ACCIÓN cruzando factores (No solo listes Fortalezas/Debilidades):

1. ESTRATEGIA FO (Maxi-Maxi):
- ¿Cómo usar una Fortaleza específica para capitalizar una Oportunidad?

2. ESTRATEGIA DO (Mini-Maxi):
- ¿Cómo minimizar una Debilidad para aprovechar una Oportunidad?

3. ESTRATEGIA FA (Maxi-Mini):
- ¿Cómo usar una Fortaleza para defenderse de una Amenaza?

4. ESTRATEGIA DA (Mini-Mini):
- ¿Cómo minimizar Debilidades para evitar Amenazas (Estrategia de supervivencia)?

Sé concreto y accionable.`,

            'blue_ocean': `Eres experto en innovación usando Blue Ocean Strategy (Kim & Mauborgne).
${commonContext}
Ventaja Competitiva actual: ${ctx.competitiveAdvantage || 'Estándar'}

Diseña una Curva de Valor Divergente usando la matriz ERIC:

ELIMINAR:
- ¿Qué factores que la industria da por sentado deberían eliminarse? (Costos innecesarios)

REDUCIR:
- ¿Qué factores deberían reducirse muy por debajo de la norma de la industria?

INCREMENTAR:
- ¿Qué factores deberían elevarse muy por encima de la norma?

CREAR:
- ¿Qué factores que la industria nunca ha ofrecido deberían crearse? (Innovación de valor)

Define el "Nuevo Océano Azul" en una frase.`,

            'gestion_riesgos': `Eres Project Manager certificado PMP (PMI Standard).
${commonContext}

Identifica los 3 RIESGOS PRINCIPALES y sus planes de respuesta:

Formato para cada riesgo:
1. RIESGO: [Descripción clara del evento incierto]
   - TIPO: (Operativo / Financiero / Legal / Mercado)
   - PROBABILIDAD: (Alta/Media/Baja)
   - IMPACTO: (Alto/Medio/Bajo)
   - ESTRATEGIA DE RESPUESTA: (Mitigar / Transferir / Aceptar / Evitar)
   - ACCIÓN CONCRETA: [Qué haremos preventiva o correctivamente]`
        };

        // Si no existe prompt específico, usar prompt genérico inteligente
        return prompts[fieldId] || `Eres consultor de negocios senior.
${commonContext}

Para el campo "${fieldId}", genera una sugerencia:
- Específica para este negocio
- Basada en mejores prácticas
- Accionable e implementable
- Máximo 4 oraciones

Responde de forma directa sin explicaciones adicionales.`;
    }
};

// Export global
window.BusinessPrompts = BusinessPrompts;
