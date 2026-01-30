-- =================================================================================
-- PROYECTO: PlanIA (Multi-User & AI Context Extensions)
-- ARCHIVO: database/schema_users.sql
-- DESCRIPCIÓN: Tablas para gestión de usuarios, roles y asignaciones.
-- =================================================================================

-- 1. TABLA DE USUARIOS (RBAC Simplificado)
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

-- 2. TABLA DE ASIGNANCIÓN DE PROYECTOS
CREATE TABLE IF NOT EXISTS project_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT UNSIGNED NOT NULL,
    advisor_id INT NOT NULL,
    assigned_by INT NOT NULL COMMENT 'Admin ID who assigned',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    
    FOREIGN KEY (project_id) REFERENCES proyectos_negocio(id_proyecto) ON DELETE CASCADE,
    FOREIGN KEY (advisor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. EXTENSIÓN PARA AI LOGS (Contexto y Sesiones)
-- Nota: Ejecutar solo si la tabla ya existe
SET @exist := (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'ai_logs' AND column_name = 'session_id');
SET @sql := IF(@exist = 0, 'ALTER TABLE ai_logs ADD COLUMN session_id VARCHAR(64) NULL AFTER user_id, ADD COLUMN context_snapshot JSON NULL AFTER metadata', 'SELECT "Column session_id already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 4. USUARIO ADMIN POR DEFECTO (Password: admin123 - DEBE CAMBIARSE EN PRODUCCIÓN)
-- Hash es para 'admin123' (ejemplo simple, en prod usar bcrypt real)
INSERT IGNORE INTO users (username, password_hash, full_name, role) 
VALUES ('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Administrador del Sistema', 'admin');
