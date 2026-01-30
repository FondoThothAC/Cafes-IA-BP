<?php
/**
 * =================================================================================
 * PROYECTO: PlanIA (Config)
 * ARCHIVO: config/database.php
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: GPLv2 (Open Source para análisis de datos públicos).
 * DESCRIPCIÓN: Configuración de conexión a la base de datos.
 * =================================================================================
 */

return [
    'host' => getenv('DB_HOST') ?: 'localhost',
    'database' => getenv('DB_NAME') ?: 'plania',
    'user' => getenv('DB_USER') ?: 'root',
    'password' => getenv('DB_PASSWORD') ?: '',
    'charset' => 'utf8mb4',
];
