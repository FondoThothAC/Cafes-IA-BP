# =================================================================================
# PROYECTO: PlanIA (Core Backend & Data Structure)
# ARCHIVO: database/schema_master.sql
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: GPLv2 (Open Source para análisis de datos públicos).
# DESCRIPCIÓN: Estructura de "Super Fila" para Planes de Negocio Híbridos.
# =================================================================================

CREATE TABLE IF NOT EXISTS proyectos_negocio (
    -- 1. IDENTIFICADORES Y METADATOS
    id_proyecto BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid_usuario VARCHAR(64) NOT NULL COMMENT 'ID del emprendedor o asesor',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    estatus_proyecto ENUM('borrador', 'revision_ia', 'completo', 'publicado') DEFAULT 'borrador',
    version_schema VARCHAR(10) DEFAULT 'v1.0',

    -- 2. PORTADA Y PRELIMINARES (Ref: SAETA / Búho)
    a1_nombre_negocio VARCHAR(255),
    a2_nombre_emprendedor VARCHAR(255),
    a3_logotipo_url VARCHAR(512) COMMENT 'URL a almacenamiento local/s3',
    a4_carta_presentacion TEXT COMMENT 'Generado o redactado manualmente',

    -- 3. UNIDAD I: RESUMEN EJECUTIVO (Ref: SAETA / Búho)
    b1_descripcion_negocio TEXT,
    b2_problema_oportunidad TEXT,
    b3_propuesta_valor TEXT COMMENT 'Qué lo hace especial',
    b4_cliente_objetivo_resumen VARCHAR(500),
    b5_monto_solicitado DECIMAL(15, 2) DEFAULT 0.00,

    -- 4. UNIDAD II: PERFIL DEL EMPRENDEDOR (Ref: SAETA / Búho)
    c1_experiencia_previa TEXT,
    c2_motivacion TEXT,
    c3_disponibilidad_tiempo VARCHAR(255),
    c4_organigrama_json JSON COMMENT 'Estructura del equipo y roles',

    -- 5. UNIDAD III: ESTUDIO DE MERCADO Y APIs (Ref: SAETA / Búho)
    d1_segmento_cliente TEXT,
    d2_necesidades_gustos TEXT,
    
    -- API HARVESTING: COMPETENCIA
    d3_competidores_json JSON COMMENT 'Lista dinámica de competidores extraída de DENUE o manual',
    d4_api_inegi_raw JSON COMMENT 'Respuesta cruda de la API DENUE para auditoría',
    d5_ventaja_competitiva TEXT,
    
    -- GEOLOCALIZACIÓN (Mapbox/Google)
    d6_latitud DECIMAL(10, 8) COMMENT 'Coordenada exacta del local',
    d7_longitud DECIMAL(11, 8),
    d8_direccion_formateada VARCHAR(512),
    d9_mapa_estatico_url VARCHAR(512) COMMENT 'Imagen generada del mapa para el PDF',

    -- 6. UNIDAD IV: ORGANIZACIÓN Y PRODUCCIÓN (Ref: SAETA / Búho)
    e1_proceso_produccion TEXT,
    e2_capacidad_produccion VARCHAR(255) COMMENT 'Ej: Pasteles por mes',
    
    -- SUPER CAMPO: INVENTARIO Y BOM (Bill of Materials)
    -- Estructura JSON esperada:
    -- [
    --   {"producto": "Pastel Chocolate", "precio_venta": 500, "insumos": [{"item": "Harina", "costo": 20}, ...]},
    --   {"producto": "Galletas", ...}
    -- ]
    e3_productos_bom_json JSON COMMENT 'Desglose técnico de productos e insumos',
    e4_proveedores_json JSON COMMENT 'Lista de proveedores con contacto',

    -- 7. UNIDAD V: MARKETING Y VENTAS (Ref: SAETA / Búho)
    f1_identidad_marca TEXT,
    f2_estrategia_precios TEXT,
    f3_canales_venta JSON COMMENT 'Checkbox list: WhatsApp, Local, Facebook, etc.',
    f4_estrategia_promocion TEXT,

    -- 8. UNIDAD VI: PLAN FINANCIERO & BANXICO (Ref: SAETA / Búho)
    -- Variables Macroeconómicas (API Banxico)
    g1_tipo_cambio_usd DECIMAL(10, 4) COMMENT 'Dato en tiempo real Banxico',
    g2_tasa_interes_tiie DECIMAL(10, 4),
    g3_inflacion_anual DECIMAL(5, 2),
    g4_fecha_datos_macro DATE COMMENT 'Fecha de la última consulta a Banxico',

    -- Cálculos del sistema (Python Local Agent los llenará)
    g5_costos_fijos_mensuales DECIMAL(15, 2),
    g6_costos_variables_unitarios JSON COMMENT 'Resumen de costos por producto',
    g7_punto_equilibrio TEXT COMMENT 'Cálculo de unidades mínimas a vender',
    g8_inversion_inicial DECIMAL(15, 2) COMMENT 'Presupuesto de arranque',
    g9_flujo_efectivo_json JSON COMMENT 'Financial parameters and monthly units',
    
    -- Proyecciones (Spreadsheet dentro del JSON)
    g9_flujo_efectivo_anual_json JSON COMMENT 'Proyección mes a mes Año 1',
    g10_rentabilidad_roi VARCHAR(100) COMMENT 'Retorno de inversión calculado',

    -- 9. UNIDAD VII: IMPACTO Y LEGAL (Ref: SAETA / Búho)
    h1_impacto_social TEXT COMMENT 'Beneficio a la comunidad/familia',
    h2_impacto_economico TEXT,
    h3_marco_legal_json JSON COMMENT 'Lista de permisos necesarios (Suelo, Salud, etc.)',

    -- 9.5 MODULE DATA (JSON storage for UI modules)
    d2_segmento_json JSON COMMENT 'Customer segment analysis data',
    g10_presupuesto_inversion_json JSON COMMENT 'Investment budget items',
    g11_proyeccion_costos_json JSON COMMENT 'Cost projection data (fixed and variable)',
    g12_proyeccion_ingresos_json JSON COMMENT 'Revenue projection data (products/services)',
    i1_clientes_json JSON COMMENT 'Customer registry data',
    i2_encuestas_json JSON COMMENT 'Survey data',
    i3_marketing_json JSON COMMENT 'Marketing metrics data',
    i4_operaciones_json JSON COMMENT 'Operations data',
    i5_cuentas_json JSON COMMENT 'Accounting data',
    i6_estado_resultados_json JSON COMMENT 'Income statement data',
    i7_identidad_json JSON COMMENT 'Brand identity (logo, colors, socials)',

    -- 10. EVIDENCIAS (URLs de archivos subidos)
    url_evidencia_1 VARCHAR(512),
    url_evidencia_2 VARCHAR(512),
    url_evidencia_3 VARCHAR(512),
    url_evidencia_4 VARCHAR(512),
    url_evidencia_5 VARCHAR(512),

    -- 11. CONTROL DE AGENTES IA (Local Connection)
    ia_flag_procesar BOOLEAN DEFAULT FALSE COMMENT 'Si TRUE, el agente local debe leer esta fila',
    ia_ultimo_log TEXT COMMENT 'Mensaje de error o éxito del agente local',
    ia_fecha_procesamiento TIMESTAMP NULL,
    data_source ENUM('API', 'Manual') DEFAULT 'Manual' COMMENT 'Origen de datos macro'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ÍNDICES PARA BÚSQUEDA RÁPIDA
CREATE INDEX idx_usuario ON proyectos_negocio(uuid_usuario);
CREATE INDEX idx_estatus ON proyectos_negocio(estatus_proyecto);
CREATE INDEX idx_geo ON proyectos_negocio(d6_latitud, d7_longitud);
