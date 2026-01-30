<?php
/**
 * =================================================================================
 * PROYECTO: CAFES - Sistema de Planes de Negocio
 * ARCHIVO: config/database.php
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: GPL-2.0-or-later
 * DESCRIPCIÓN: Configuración de conexión a la base de datos CAFES (Docker).
 * =================================================================================
 */

return [
    'host' => getenv('DB_HOST') ?: 'localhost',
    'database' => getenv('DB_NAME') ?: 'plania',
    'user' => getenv('DB_USER') ?: 'plania_user',
    'password' => getenv('DB_PASSWORD') ?: 'plania_pass_2026',
    'charset' => 'utf8mb4',
];
