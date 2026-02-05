# =================================================================================
# PROYECTO: PlanIA (Prompts Library)
# ARCHIVO: modules/prompts/__init__.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Librería de prompts para el agente Bob, organizados por industria
#              y tipo de campo.
# =================================================================================

from typing import Dict, Any

# ==============================================================================
# BASE PROMPT TEMPLATE
# ==============================================================================

BASE_SYSTEM_PROMPT = """Eres Bob, un experto consultor de negocios con especialización en:
- Metodología Lean Startup (Eric Ries)
- Modelo Delta (Arnoldo Hax, MIT)
- Business Model Canvas (Osterwalder)
- 5 Fuerzas de Porter y estrategias competitivas

Tu rol es ayudar a emprendedores mexicanos a completar sus planes de negocio.
Siempre considera:
1. El contexto económico de México
2. Las normativas aplicables (NOMs, permisos)
3. Los estándares de la industria
4. La etapa del negocio (micro, startup, empresa)

Responde SIEMPRE en español, de manera concisa y accionable.
"""

# ==============================================================================
# FIELD-SPECIFIC PROMPTS
# ==============================================================================

FIELD_PROMPTS = {
    # -------------------------------------------------------------------------
    # IDENTIDAD DEL NEGOCIO
    # -------------------------------------------------------------------------
    "a1_nombre_negocio": {
        "system": BASE_SYSTEM_PROMPT,
        "user": """Sugiere 3 nombres creativos y memorables para un negocio con las siguientes características:
- Giro: {giro}
- Ubicación: {ubicacion}
- Propuesta de valor: {propuesta_valor}
- Público objetivo: {publico_objetivo}

Los nombres deben ser:
1. Fáciles de pronunciar y recordar
2. Disponibles como dominio .com o .mx (evita nombres muy comunes)
3. Que transmitan la esencia del negocio

Formato de respuesta:
1. [NOMBRE] - [Razón/significado]
2. [NOMBRE] - [Razón/significado]
3. [NOMBRE] - [Razón/significado]
"""
    },
    
    "b1_vision": {
        "system": BASE_SYSTEM_PROMPT,
        "user": """Crea una declaración de VISIÓN para {nombre_negocio}.

Contexto del negocio:
- Descripción: {descripcion}
- Industria: {industria}
- Complejidad: {complejidad}

La visión debe:
- Ser inspiradora y a largo plazo (5-10 años)
- Describir el impacto deseado en la comunidad/industria
- Ser clara y memorable

Responde SOLO con la declaración de visión, sin explicaciones adicionales.
"""
    },
    
    "b2_mision": {
        "system": BASE_SYSTEM_PROMPT,
        "user": """Crea una declaración de MISIÓN para {nombre_negocio}.

Contexto del negocio:
- Descripción: {descripcion}
- Público objetivo: {segmento_cliente}
- Propuesta de valor: {propuesta_valor}

La misión debe responder:
- ¿Qué hacemos?
- ¿Para quién lo hacemos?
- ¿Cómo lo hacemos?
- ¿Por qué lo hacemos?

Responde SOLO con la declaración de misión, sin explicaciones adicionales.
"""
    },
    
    "b3_propuesta_valor": {
        "system": BASE_SYSTEM_PROMPT,
        "user": """Crea una PROPUESTA DE VALOR única para {nombre_negocio}.

Contexto:
- Descripción: {descripcion}
- Segmento de cliente: {segmento_cliente}
- Competidores conocidos: {competidores}
- Problema que resuelve: {problema_cliente}

Sigue el formato de Geoffrey Moore:
"Para [cliente objetivo] que [necesidad/problema], [nombre del producto] es [categoría] 
que [beneficio principal]. A diferencia de [competencia], nuestro producto [diferenciador único]."

Responde SOLO con la propuesta de valor, sin explicaciones.
"""
    },
    
    # -------------------------------------------------------------------------
    # MERCADO
    # -------------------------------------------------------------------------
    "d1_segmento_cliente": {
        "system": BASE_SYSTEM_PROMPT,
        "user": """Define el SEGMENTO DE CLIENTE ideal para {nombre_negocio}.

Contexto:
- Descripción: {descripcion}
- Ubicación: {ubicacion}
- Productos/servicios: {productos}

Incluye:
1. Demografía (edad, género, ubicación, ingresos)
2. Psicografía (valores, intereses, estilo de vida)
3. Comportamiento de compra
4. Problema principal que resuelves
5. Tamaño estimado del segmento

Formato estructurado con viñetas.
"""
    },
    
    "d3_competidores_json": {
        "system": BASE_SYSTEM_PROMPT,
        "user": """Identifica los COMPETIDORES principales para {nombre_negocio}.

Contexto:
- Industria: {industria}
- Ubicación: {ubicacion}
- Tipo de negocio: {tipo_negocio}

Para cada competidor proporciona:
1. Nombre
2. Tipo (directo/indirecto/sustituto)
3. Fortalezas
4. Debilidades
5. Precio aproximado

Responde en formato JSON:
[
  {{"nombre": "...", "tipo": "directo", "fortalezas": "...", "debilidades": "...", "precio": "$XX"}}
]
"""
    },
    
    "d5_ventaja_competitiva": {
        "system": BASE_SYSTEM_PROMPT + """
Metodología adicional:
- Best Product: Liderazgo en costos o diferenciación
- Total Customer Solution: Solución integral al cliente
- System Lock-In: Bloqueo del sistema/ecosistema
""",
        "user": """Define la VENTAJA COMPETITIVA sostenible de {nombre_negocio}.

Contexto:
- Descripción: {descripcion}
- Competidores: {competidores}
- Propuesta de valor: {propuesta_valor}
- Posición Delta sugerida: {delta_position}

Explica:
1. ¿Cuál es la ventaja competitiva principal?
2. ¿Por qué es difícil de copiar?
3. ¿Cómo se alinea con la posición estratégica Delta?
4. ¿Cuánto tiempo se puede mantener?

Formato: Párrafos cortos y claros.
"""
    },
    
    # -------------------------------------------------------------------------
    # FINANZAS
    # -------------------------------------------------------------------------
    "g8_inversion_inicial": {
        "system": BASE_SYSTEM_PROMPT + """
Tienes acceso a datos de referencia de la industria mexicana.
""",
        "user": """Calcula la INVERSIÓN INICIAL necesaria para {nombre_negocio}.

Contexto:
- Industria: {industria}
- Ubicación: {ubicacion}
- Tamaño esperado: {tamano}
- Complejidad: {complejidad}

Datos de referencia de la industria:
{industria_referencia}

Desglosa por categorías:
1. Remodelación/obra civil
2. Equipo y maquinaria
3. Mobiliario
4. Inventario inicial
5. Licencias y permisos
6. Capital de trabajo (3 meses)
7. Otros/imprevistos (10%)

Responde con:
- Tabla de desglose
- Total estimado
- Rango (mínimo - máximo)

Al final, indica SOLO el número total como valor para la base de datos.
"""
    },
    
    "g5_costos_fijos_mensuales": {
        "system": BASE_SYSTEM_PROMPT,
        "user": """Calcula los COSTOS FIJOS MENSUALES para {nombre_negocio}.

Contexto:
- Industria: {industria}
- Ubicación: {ubicacion}
- Inversión inicial: ${inversion_inicial}
- Número de empleados: {num_empleados}

Datos de referencia:
{industria_referencia}

Incluye:
1. Renta (basado en ubicación y tamaño)
2. Nómina (con cargas sociales IMSS ~35%)
3. Servicios (luz, agua, gas, internet)
4. Marketing/publicidad
5. Contabilidad/legal
6. Seguros
7. Mantenimiento
8. Otros

Responde con tabla y total mensual.
"""
    },
    
    "g6_punto_equilibrio": {
        "system": BASE_SYSTEM_PROMPT,
        "user": """Calcula el PUNTO DE EQUILIBRIO para {nombre_negocio}.

Datos disponibles:
- Costos fijos mensuales: ${costos_fijos}
- Precio promedio de venta: ${precio_promedio}
- Costo variable unitario: ${costo_variable}
- Margen de contribución: {margen_contribucion}%

Fórmula:
Punto de Equilibrio = Costos Fijos / Margen de Contribución

Calcula:
1. Punto de equilibrio en ventas ($)
2. Punto de equilibrio en unidades
3. Punto de equilibrio en días (si vendes X unidades/día)

Incluye gráfica conceptual ASCII si es posible.
"""
    },
    
    "g7_roi_esperado": {
        "system": BASE_SYSTEM_PROMPT,
        "user": """Calcula el ROI ESPERADO y tiempo de recuperación para {nombre_negocio}.

Datos:
- Inversión inicial: ${inversion_inicial}
- Costos fijos mensuales: ${costos_fijos}
- Ingresos proyectados mensuales: ${ingresos_mensuales}
- Margen bruto: {margen_bruto}%

Calcula:
1. Utilidad mensual proyectada
2. Tiempo de recuperación de inversión (meses)
3. ROI anual (%)
4. VPN a 3 años (tasa descuento 12%)

Responde con el número de meses para recuperar inversión.
"""
    },
    
    # -------------------------------------------------------------------------
    # ORGANIZACIÓN
    # -------------------------------------------------------------------------
    "c4_organigrama_json": {
        "system": BASE_SYSTEM_PROMPT + """
Conoces las clases de riesgo IMSS y salarios promedio en México.
""",
        "user": """Diseña el ORGANIGRAMA recomendado para {nombre_negocio}.

Contexto:
- Industria: {industria}
- Tamaño: {tamano}
- Complejidad: {complejidad}
- Inversión: ${inversion_inicial}

Datos de salarios de la industria:
{industria_referencia}

Para cada puesto incluye:
1. Título del puesto
2. Salario mensual bruto
3. Número de personas necesarias
4. Clase de riesgo IMSS (I-V)

Responde en formato JSON:
[
  {{"title": "Gerente General", "salary": 25000, "count": 1, "riskClass": "I"}},
  {{"title": "...", ...}}
]

Considera mantener el costo de nómina < 30-35% de los ingresos esperados.
"""
    },
    
    # -------------------------------------------------------------------------
    # PRODUCTOS
    # -------------------------------------------------------------------------
    "g12_proyeccion_ingresos_json": {
        "system": BASE_SYSTEM_PROMPT,
        "user": """Crea la PROYECCIÓN DE INGRESOS para {nombre_negocio}.

Contexto:
- Industria: {industria}
- Descripción: {descripcion}
- Capacidad de producción: {capacidad}
- Ubicación: {ubicacion}

Datos de precios de mercado:
{industria_referencia}

Para cada producto/servicio principal, incluye:
1. Nombre del producto
2. Precio de venta unitario
3. Costo variable unitario
4. Cantidad estimada mensual
5. Ingreso mensual

Responde en formato JSON:
[
  {{
    "nombre_producto": "...",
    "precio": 100,
    "costo_unitario": 40,
    "cantidad_mensual": 500,
    "ingreso_mensual": 50000
  }}
]

Incluye al menos 3-5 productos principales que representen el 80% de los ingresos.
"""
    },
    
    "e1_proceso_produccion": {
        "system": BASE_SYSTEM_PROMPT,
        "user": """Describe el PROCESO DE PRODUCCIÓN para {nombre_negocio}.

Contexto:
- Industria: {industria}
- Productos principales: {productos}
- Capacidad esperada: {capacidad}

Normativas aplicables:
{normativas}

Incluye:
1. Diagrama de flujo del proceso (descripción)
2. Etapas principales con tiempos estimados
3. Puntos críticos de control (calidad, seguridad)
4. Equipo necesario en cada etapa
5. Personal requerido por etapa

Formato: Lista numerada con subitems.
"""
    }
}


# ==============================================================================
# INDUSTRY-SPECIFIC ADDITIONS
# ==============================================================================

INDUSTRY_PROMPT_ADDITIONS = {
    "panaderia": {
        "context": """
Datos específicos de panaderías en México:
- Margen bruto típico: 50-60%
- NOM aplicable: NOM-251-SSA1-2009
- Clase de riesgo IMSS: II
- Horarios típicos: 5:00 AM - 8:00 PM
- Temporadas altas: Día de Muertos, Reyes, Navidad
""",
        "keywords": ["fermentación", "horneado", "masa madre", "pan artesanal"]
    },
    
    "restaurante": {
        "context": """
Datos específicos de restaurantes en México:
- Food cost objetivo: 28-35%
- Labor cost objetivo: 25-30%
- Prime cost: < 65%
- Distintivo H recomendado
- NOMs: NOM-251-SSA1, NOM-093-SSA1
- Rotación de mesas: 2-4 veces/servicio
""",
        "keywords": ["menú", "servicio", "cocina", "comensales", "ticket"]
    },
    
    "tecnologia": {
        "context": """
Datos específicos de startups tecnológicas en México:
- Modelo de ingresos común: SaaS (suscripción)
- Métricas clave: MRR, Churn, LTV, CAC
- Regulación: Ley Fintech (si aplica)
- Fuentes de financiamiento: ángeles, VC, gobierno
- Hub principal: CDMX, GDL, MTY
""",
        "keywords": ["MVP", "escalabilidad", "usuarios activos", "runway"]
    }
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_prompt_for_field(field: str, context: Dict[str, Any]) -> Dict[str, str]:
    """
    Obtiene el prompt completo para un campo específico.
    
    Args:
        field: Nombre del campo de la BD
        context: Diccionario con variables para interpolación
        
    Returns:
        Dict con 'system' y 'user' prompts listos para usar
    """
    if field not in FIELD_PROMPTS:
        # Generic fallback
        return {
            "system": BASE_SYSTEM_PROMPT,
            "user": f"Genera contenido apropiado para el campo '{field}' de un plan de negocios.\n\nContexto: {context}"
        }
    
    prompt = FIELD_PROMPTS[field].copy()
    
    # Add industry-specific context if available
    industry = context.get("industria", "general")
    if industry in INDUSTRY_PROMPT_ADDITIONS:
        prompt["system"] += "\n\n" + INDUSTRY_PROMPT_ADDITIONS[industry]["context"]
    
    # Interpolate variables in user prompt
    try:
        prompt["user"] = prompt["user"].format(**context)
    except KeyError as e:
        # If a variable is missing, leave placeholder
        pass
    
    return prompt


def get_fields_for_module(module: str) -> list:
    """Obtiene la lista de campos para un módulo específico."""
    modules_fields = {
        "identidad": ["a1_nombre_negocio", "b1_vision", "b2_mision", "b3_propuesta_valor"],
        "mercado": ["d1_segmento_cliente", "d3_competidores_json", "d5_ventaja_competitiva"],
        "finanzas": ["g8_inversion_inicial", "g5_costos_fijos_mensuales", "g6_punto_equilibrio", "g7_roi_esperado"],
        "organizacion": ["c4_organigrama_json"],
        "productos": ["g12_proyeccion_ingresos_json", "e1_proceso_produccion"]
    }
    return modules_fields.get(module, [])
