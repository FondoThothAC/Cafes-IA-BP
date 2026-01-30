<?php
/**
 * ================================================================================
 * PROYECTO: CAFES - Sistema de Planes de Negocio
 * ARCHIVO:  scripts/import_to_database.php
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: GPL-2.0-or-later
 * DESCRIPCIÓN: Script para importar proyectos JSON a la base de datos CAFES
 * ================================================================================
 */

// Configuración
$PROJECTS_DIR = __DIR__ . '/../data/imported_projects';
$UUID_USUARIO = 'cafes-import-2026';

// Cargar configuración de base de datos
$config = require_once __DIR__ . '/../config/database.php';

echo "============================================================\n";
echo "CAFES - Importador de Proyectos a Base de Datos\n";
echo "============================================================\n\n";

// Conectar a la base de datos
try {
    $dsn = "mysql:host={$config['host']};dbname={$config['database']};charset=utf8mb4";
    $pdo = new PDO($dsn, $config['user'], $config['password'], [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    ]);
    echo "✅ Conectado a: {$config['database']}\n\n";
} catch (PDOException $e) {
    die("❌ Error de conexión: " . $e->getMessage() . "\n");
}

// Leer archivo con todos los proyectos
$allProjectsFile = $PROJECTS_DIR . '/_all_projects.json';
if (!file_exists($allProjectsFile)) {
    die("❌ No se encontró _all_projects.json\n");
}

$projects = json_decode(file_get_contents($allProjectsFile), true);
echo "Proyectos a importar: " . count($projects) . "\n\n";

$imported = 0;
$errors = 0;

foreach ($projects as $i => $project) {
    $num = $i + 1;
    $nombre = $project['a1_nombre_negocio'] ?? 'Sin nombre';

    echo "[{$num}/" . count($projects) . "] {$nombre}...\n";

    try {
        // Preparar datos (truncar campos largos para evitar errores)
        $data = [
            'uuid_usuario' => $UUID_USUARIO,
            'estatus_proyecto' => 'borrador',
            'a1_nombre_negocio' => substr($nombre, 0, 200),
            'b1_descripcion_negocio' => substr($project['b1_descripcion_negocio'] ?? '', 0, 5000),
            'b2_problema_oportunidad' => substr($project['b2_problema_oportunidad'] ?? '', 0, 2000),
            'b3_propuesta_valor' => substr($project['b3_propuesta_valor'] ?? '', 0, 2000),
            'b4_cliente_objetivo_resumen' => substr($project['b4_cliente_objetivo_resumen'] ?? '', 0, 500),
            'g8_inversion_inicial' => $project['g8_inversion_inicial'] ?? 0,
            'g5_costos_fijos_mensuales' => $project['g5_costos_fijos_mensuales'] ?? 0,
            'e3_productos_bom_json' => json_encode($project['e3_productos_bom_json'] ?? [], JSON_UNESCAPED_UNICODE),
            'd3_competidores_json' => json_encode($project['d3_competidores_json'] ?? [], JSON_UNESCAPED_UNICODE),
        ];

        // Verificar si ya existe
        $stmt = $pdo->prepare("SELECT id_proyecto FROM proyectos_negocio WHERE a1_nombre_negocio = ? AND uuid_usuario = ?");
        $stmt->execute([$nombre, $UUID_USUARIO]);
        $existing = $stmt->fetch();

        if ($existing) {
            // Actualizar
            $sql = "UPDATE proyectos_negocio SET 
                b1_descripcion_negocio = :b1_descripcion_negocio,
                b4_cliente_objetivo_resumen = :b4_cliente_objetivo_resumen,
                g8_inversion_inicial = :g8_inversion_inicial,
                g5_costos_fijos_mensuales = :g5_costos_fijos_mensuales,
                e3_productos_bom_json = :e3_productos_bom_json
                WHERE id_proyecto = :id";
            $data['id'] = $existing['id_proyecto'];
            $pdo->prepare($sql)->execute($data);
            echo "   → Actualizado (ID: {$existing['id_proyecto']})\n";
        } else {
            // Insertar nuevo
            $fields = array_keys($data);
            $placeholders = array_map(fn($f) => ":$f", $fields);
            $sql = "INSERT INTO proyectos_negocio (" . implode(', ', $fields) . ") 
                    VALUES (" . implode(', ', $placeholders) . ")";
            $pdo->prepare($sql)->execute($data);
            $newId = $pdo->lastInsertId();
            echo "   → Creado (ID: {$newId})\n";
        }

        $imported++;

    } catch (Exception $e) {
        echo "   ❌ Error: " . $e->getMessage() . "\n";
        $errors++;
    }
}

echo "\n============================================================\n";
echo "✅ Importados: {$imported}\n";
echo "❌ Errores: {$errors}\n";
echo "============================================================\n";
