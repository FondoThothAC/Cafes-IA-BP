-- =================================================================================
-- PROYECTO: PlanIA (Restauración de Esquema y Usuarios)
-- =================================================================================

-- 1. TABLA MAESTRA DE PROYECTOS (schema_master.sql)
CREATE TABLE IF NOT EXISTS proyectos_negocio (
    id_proyecto BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid_usuario VARCHAR(64) NOT NULL COMMENT 'ID del emprendedor o asesor',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    estatus_proyecto ENUM('borrador', 'revision_ia', 'completo', 'publicado') DEFAULT 'borrador',
    version_schema VARCHAR(10) DEFAULT 'v1.0',
    a1_nombre_negocio VARCHAR(255),
    a2_nombre_emprendedor VARCHAR(255),
    a3_logotipo_url VARCHAR(512),
    a4_carta_presentacion TEXT,
    b1_descripcion_negocio TEXT,
    b2_problema_oportunidad TEXT,
    b3_propuesta_valor TEXT,
    b4_cliente_objetivo_resumen VARCHAR(500),
    b5_monto_solicitado DECIMAL(15, 2) DEFAULT 0.00,
    c1_experiencia_previa TEXT,
    c2_motivacion TEXT,
    c3_disponibilidad_tiempo VARCHAR(255),
    c4_organigrama_json JSON,
    d1_segmento_cliente TEXT,
    d2_necesidades_gustos TEXT,
    d3_competidores_json JSON,
    d4_api_inegi_raw JSON,
    d5_ventaja_competitiva TEXT,
    d6_latitud DECIMAL(10, 8),
    d7_longitud DECIMAL(11, 8),
    d8_direccion_formateada VARCHAR(512),
    d9_mapa_estatico_url VARCHAR(512),
    e1_proceso_produccion TEXT,
    e2_capacidad_produccion VARCHAR(255),
    e3_productos_bom_json JSON,
    e4_proveedores_json JSON,
    f1_identidad_marca TEXT,
    f2_estrategia_precios TEXT,
    f3_canales_venta JSON,
    f4_estrategia_promocion TEXT,
    g1_tipo_cambio_usd DECIMAL(10, 4),
    g2_tasa_interes_tiie DECIMAL(10, 4),
    g3_inflacion_anual DECIMAL(5, 2),
    g4_fecha_datos_macro DATE,
    g5_costos_fijos_mensuales DECIMAL(15, 2),
    g6_costos_variables_unitarios JSON,
    g7_punto_equilibrio TEXT,
    g8_inversion_inicial DECIMAL(15, 2),
    g9_flujo_efectivo_json JSON,
    g9_flujo_efectivo_anual_json JSON,
    g10_rentabilidad_roi VARCHAR(100),
    h1_impacto_social TEXT,
    h2_impacto_economico TEXT,
    h3_marco_legal_json JSON,
    d2_segmento_json JSON,
    g10_presupuesto_inversion_json JSON,
    g11_proyeccion_costos_json JSON,
    g12_proyeccion_ingresos_json JSON,
    i1_clientes_json JSON,
    i2_encuestas_json JSON,
    i3_marketing_json JSON,
    i4_operaciones_json JSON,
    i5_cuentas_json JSON,
    i6_estado_resultados_json JSON,
    i7_identidad_json JSON,
    url_evidencia_1 VARCHAR(512),
    url_evidencia_2 VARCHAR(512),
    url_evidencia_3 VARCHAR(512),
    url_evidencia_4 VARCHAR(512),
    url_evidencia_5 VARCHAR(512),
    agent_context_md LONGTEXT,
    agent_complexity ENUM('micro', 'startup', 'enterprise') DEFAULT 'micro',
    ia_flag_procesar BOOLEAN DEFAULT FALSE,
    ia_ultimo_log TEXT,
    ia_fecha_procesamiento TIMESTAMP NULL,
    data_source ENUM('API', 'Manual') DEFAULT 'Manual'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_usuario ON proyectos_negocio(uuid_usuario);
CREATE INDEX idx_estatus ON proyectos_negocio(estatus_proyecto);
CREATE INDEX idx_geo ON proyectos_negocio(d6_latitud, d7_longitud);

-- 2. TABLA DE USUARIOS (schema_users.sql)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('admin', 'asesor', 'emprendedor') NOT NULL DEFAULT 'emprendedor',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. ASIGNACIONES
CREATE TABLE IF NOT EXISTS project_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT UNSIGNED NOT NULL,
    advisor_id INT NOT NULL,
    assigned_by INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (project_id) REFERENCES proyectos_negocio(id_proyecto) ON DELETE CASCADE,
    FOREIGN KEY (advisor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. INSERTAR USUARIOS SOLICITADOS (Password: PlanIA2026)
INSERT IGNORE INTO users (username, password_hash, full_name, role) VALUES 
('celis', '$2y$10$FyndsII2jDKy.BuOa5.Siet7rAc1LagsFw9lparFa82kmUrNEcNJi', 'Celis', 'admin'),
('segura', '$2y$10$FyndsII2jDKy.BuOa5.Siet7rAc1LagsFw9lparFa82kmUrNEcNJi', 'Segura', 'admin'),
('castillo', '$2y$10$FyndsII2jDKy.BuOa5.Siet7rAc1LagsFw9lparFa82kmUrNEcNJi', 'Castillo', 'admin'),
('yaretzy', '$2y$10$FyndsII2jDKy.BuOa5.Siet7rAc1LagsFw9lparFa82kmUrNEcNJi', 'Yaretzy', 'asesor'),
('edwin', '$2y$10$FyndsII2jDKy.BuOa5.Siet7rAc1LagsFw9lparFa82kmUrNEcNJi', 'Edwin', 'asesor'),
('darinka', '$2y$10$FyndsII2jDKy.BuOa5.Siet7rAc1LagsFw9lparFa82kmUrNEcNJi', 'Darinka', 'asesor'),
('heidi', '$2y$10$FyndsII2jDKy.BuOa5.Siet7rAc1LagsFw9lparFa82kmUrNEcNJi', 'Heidi', 'asesor'),
('angel', '$2y$10$FyndsII2jDKy.BuOa5.Siet7rAc1LagsFw9lparFa82kmUrNEcNJi', 'Angel', 'asesor'),
('nico', '$2y$10$FyndsII2jDKy.BuOa5.Siet7rAc1LagsFw9lparFa82kmUrNEcNJi', 'Nico', 'asesor');
