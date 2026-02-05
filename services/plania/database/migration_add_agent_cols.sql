-- Migración para soporte de Agente IA (Fase 2 y 6)
-- Agrega columnas para contexto, logs, fecha de procesamiento y complejidad.

ALTER TABLE proyectos_negocio
ADD COLUMN agent_context_md LONGTEXT COMMENT 'Contexto acumulado del agente Bob (Markdown)',
ADD COLUMN agent_complexity ENUM('micro', 'startup', 'enterprise') DEFAULT 'micro' COMMENT 'Complejidad determinada por el agente',
ADD COLUMN ia_flag_procesar BOOLEAN DEFAULT FALSE COMMENT 'Si TRUE, el agente local debe leer esta fila',
ADD COLUMN ia_ultimo_log TEXT COMMENT 'Mensaje de error o éxito del agente local',
ADD COLUMN ia_fecha_procesamiento TIMESTAMP NULL,
ADD COLUMN data_source ENUM('API', 'Manual') DEFAULT 'Manual' COMMENT 'Origen de datos macro';

-- Índices recomendados si no existen
CREATE INDEX idx_ia_flag ON proyectos_negocio(ia_flag_procesar);
