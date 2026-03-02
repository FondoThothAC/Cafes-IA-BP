<?php
/**
 * =================================================================================
 * PROYECTO: PlanIA (Backend API)
 * ARCHIVO: public/save_row.php
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: GPLv2 (Open Source para análisis de datos públicos).
 * DESCRIPCIÓN: API endpoint para guardar/actualizar filas de proyectos.
 * =================================================================================
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Load database configuration
$config = require_once __DIR__ . '/../config/database.php';

/**
 * Connect to MySQL database
 */
function getConnection($config)
{
    try {
        $dsn = "mysql:host={$config['host']};dbname={$config['database']};charset=utf8mb4";
        $pdo = new PDO($dsn, $config['user'], $config['password'], [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
        ]);
        return $pdo;
    } catch (PDOException $e) {
        error_log("Database connection error: " . $e->getMessage());
        error_log("DSN: " . $dsn);
        http_response_code(500);
        echo json_encode([
            'error' => 'Database connection failed',
            'message' => $e->getMessage(),
            'code' => $e->getCode()
        ]);
        exit();
    }
}

/**
 * Validate and sanitize input data
 */
function sanitizeInput($data)
{
    $sanitized = [];

    // List of allowed fields (mapped to DB columns)
    $allowedFields = [
        'uuid_usuario',
        'uuid_consultor', // RBAC field
        'estatus_proyecto',
        'a1_nombre_negocio',
        'a2_nombre_emprendedor',
        'a3_logotipo_url',
        'a4_carta_presentacion',
        'b1_descripcion_negocio',
        'b2_problema_oportunidad',
        'b3_propuesta_valor',
        'b4_cliente_objetivo_resumen',
        'b5_monto_solicitado',
        'c1_experiencia_previa',
        'c2_motivacion',
        'c3_disponibilidad_tiempo',
        'c4_organigrama_json',
        'd1_segmento_cliente',
        'd2_necesidades_gustos',
        'd3_competidores_json',
        'd5_ventaja_competitiva',
        'd6_latitud',
        'd7_longitud',
        'd8_direccion_formateada',
        'd6_analisis_mercado_json',
        'e1_proceso_produccion',
        'e2_capacidad_produccion',
        'e3_productos_bom_json',
        'e4_proveedores_json',
        'f1_identidad_marca',
        'f2_estrategia_precios',
        'f3_canales_venta',
        'f4_estrategia_promocion',
        'g5_costos_fijos_mensuales',
        'g8_inversion_inicial',
        'g9_flujo_efectivo_json',
        'g10_presupuesto_inversion_json',
        'g11_proyeccion_costos_json',
        'g12_proyeccion_ingresos_json',
        'd2_segmento_json',
        'h1_impacto_social',
        'h2_impacto_economico',
        'h3_marco_legal_json',
        'i1_clientes_json',
        'i2_encuestas_json',
        'i3_marketing_json',
        'i4_operaciones_json',
        'i5_cuentas_json',
        'i6_estado_resultados_json',
        'i7_identidad_json',
        'url_evidencia_1',
        'url_evidencia_2',
        'url_evidencia_3',
        'url_evidencia_4',
        'url_evidencia_5',
        'ia_flag_procesar',
        // Marketing Plan Fields (Patch v1.2.2)
        'h1_estrategia_precio',
        'h2_precio_promedio',
        'h3_margen_objetivo',
        'h4_justificacion_precio',
        'h5_canales_distribucion',
        'h6_canal_principal',
        'h7_tacticas_promocion',
        'h8_presupuesto_marketing',
        'h9_pct_marketing',
        'h10_funnel_awareness',
        'h11_funnel_consideracion',
        'h12_funnel_intencion',
        'h13_funnel_compra',
        'h14_cac_objetivo',
        'h15_clv_objetivo',
        'h16_roas_objetivo',
        // --- Added for Units III, VII, VIII, IX ---
        'g9_uso_capital',
        'h4_compromiso',
        'i1_pestel_analisis',
        'i2_tows_matrix',
        'i3_blue_ocean',
        'i4_gestion_riesgos'
    ];

    // Explicit list of JSON columns in the database (includes those without _json suffix)
    $jsonFields = [
        'f3_canales_venta',  // JSON type in DB but no _json suffix
        'c4_organigrama_json',
        'd3_competidores_json',
        'd4_api_inegi_raw',
        'e3_productos_bom_json',
        'e4_proveedores_json',
        'g6_costos_variables_unitarios',
        'g9_flujo_efectivo_json',
        'g9_flujo_efectivo_anual_json',
        'h3_marco_legal_json',
        'd2_segmento_json',
        'g10_presupuesto_inversion_json',
        'g11_proyeccion_costos_json',
        'g12_proyeccion_ingresos_json',
        'i1_clientes_json',
        'i2_encuestas_json',
        'i3_marketing_json',
        'i4_operaciones_json',
        'i5_cuentas_json',
        'i6_estado_resultados_json',
        'i7_identidad_json',
        'd6_analisis_mercado_json'
    ];

    foreach ($allowedFields as $field) {
        if (isset($data[$field])) {
            $value = $data[$field];

            // Skip empty values entirely (will be NULL in DB)
            if ($value === '' || $value === null) {
                continue;
            }

            // Handle JSON fields (explicit list OR _json suffix)
            if (in_array($field, $jsonFields) || strpos($field, '_json') !== false) {
                // If it's already valid JSON, use it; otherwise, wrap as JSON string
                if (is_string($value)) {
                    json_decode($value);
                    if (json_last_error() === JSON_ERROR_NONE) {
                        $sanitized[$field] = $value; // Already valid JSON
                    } else {
                        $sanitized[$field] = json_encode($value, JSON_UNESCAPED_UNICODE); // Wrap as JSON string
                    }
                } else {
                    $sanitized[$field] = json_encode($value, JSON_UNESCAPED_UNICODE);
                }
            }
            // Handle numeric fields
            elseif (
                in_array($field, [
                    'b5_monto_solicitado',
                    'd6_latitud',
                    'd7_longitud',
                    'g5_costos_fijos_mensuales',
                    'g8_inversion_inicial',
                    'h2_precio_promedio',
                    'h3_margen_objetivo',
                    'h8_presupuesto_marketing',
                    'h9_pct_marketing',
                    'h10_funnel_awareness',
                    'h11_funnel_consideracion',
                    'h12_funnel_intencion',
                    'h13_funnel_compra',
                    'h14_cac_objetivo',
                    'h15_clv_objetivo',
                    'h16_roas_objetivo'
                ])
            ) {
                $sanitized[$field] = is_numeric($value) ? floatval($value) : 0;
            }
            // Handle boolean fields
            elseif ($field === 'ia_flag_procesar') {
                $sanitized[$field] = filter_var($value, FILTER_VALIDATE_BOOLEAN) ? 1 : 0;
            }
            // Default: sanitize as string
            else {
                $sanitized[$field] = htmlspecialchars(trim($value), ENT_QUOTES, 'UTF-8');
            }
        }
    }

    return $sanitized;
}

/**
 * Insert a new project row
 */
function insertProject($pdo, $data)
{
    $fields = array_keys($data);
    $placeholders = array_map(fn($f) => ":$f", $fields);

    $sql = "INSERT INTO proyectos_negocio (" . implode(', ', $fields) . ") VALUES (" . implode(', ', $placeholders) . ")";

    $stmt = $pdo->prepare($sql);
    $stmt->execute($data);

    return $pdo->lastInsertId();
}

/**
 * Update an existing project row
 */
function updateProject($pdo, $id, $data)
{
    // Build SET clause from data keys only
    $setClause = implode(', ', array_map(fn($f) => "$f = :$f", array_keys($data)));

    $sql = "UPDATE proyectos_negocio SET $setClause WHERE id_proyecto = :id_val";

    // Add ID to params array with a unique key to avoid collision
    $params = $data;
    $params['id_val'] = $id;

    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);

    return $stmt->rowCount();
}

/**
 * Get a single project by ID
 */
function getProject($pdo, $id)
{
    $stmt = $pdo->prepare("SELECT * FROM proyectos_negocio WHERE id_proyecto = :id");
    $stmt->execute(['id' => $id]);
    return $stmt->fetch();
}

/**
 * Get all projects based on Role RBAC
 */
function getProjectsByRole($pdo, $uuid, $role)
{
    if ($role === 'admin') {
        // Admin sees EVERYTHING
        $stmt = $pdo->prepare("SELECT * FROM proyectos_negocio ORDER BY fecha_actualizacion DESC");
        $stmt->execute();
    } elseif ($role === 'consultor') {
        // Consultant sees projects ASSIGNED to them
        $stmt = $pdo->prepare("SELECT * FROM proyectos_negocio WHERE uuid_consultor = :uuid ORDER BY fecha_actualizacion DESC");
        $stmt->execute(['uuid' => $uuid]);
    } else {
        // Entrepreneur (default) sees only THEIR OWN projects
        $stmt = $pdo->prepare("SELECT * FROM proyectos_negocio WHERE uuid_usuario = :uuid ORDER BY fecha_actualizacion DESC");
        $stmt->execute(['uuid' => $uuid]);
    }
    return $stmt->fetchAll();
}

// ==================================================
// MAIN REQUEST HANDLER
// ==================================================

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed. Use POST.']);
    exit();
}

// Parse JSON input
$input = json_decode(file_get_contents('php://input'), true);

if (!$input) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON input']);
    exit();
}

// Aliases for mismatched HTML tags to match DB Columns
if (isset($input['c1_experiencia_habilidades'])) {
    $input['c1_experiencia_previa'] = $input['c1_experiencia_habilidades'];
}
if (isset($input['c3_compromiso_tiempo'])) {
    $input['c3_disponibilidad_tiempo'] = $input['c3_compromiso_tiempo'];
}
if (isset($input['f1_nombre_marca'])) {
    $input['f1_identidad_marca'] = $input['f1_nombre_marca'];
}

$pdo = getConnection($config);

// Determine action: create or update
$action = $input['action'] ?? 'create';
$projectId = $input['id_proyecto'] ?? null;

switch ($action) {
    case 'create':
        try {
            $data = sanitizeInput($input);
            if (empty($data['uuid_usuario'])) {
                throw new Exception('uuid_usuario is required');
            }
            $newId = insertProject($pdo, $data);
            echo json_encode(['success' => true, 'id_proyecto' => $newId]);
        } catch (Exception $e) {
            http_response_code(500);
            echo json_encode(['error' => $e->getMessage(), 'trace' => $e->getTraceAsString()]);
        }
        break;

    case 'update':
        try {
            if (!$projectId) {
                throw new Exception('id_proyecto is required for update');
            }
            $data = sanitizeInput($input);
            $affected = updateProject($pdo, $projectId, $data);
            echo json_encode(['success' => true, 'affected_rows' => $affected]);
        } catch (Exception $e) {
            http_response_code(500);
            echo json_encode(['error' => $e->getMessage(), 'trace' => $e->getTraceAsString()]);
        }
        break;

    case 'get':
        $project = getProject($pdo, $projectId);
        echo json_encode($project ?: ['error' => 'Project not found']);
        break;

    case 'list':
        $uuid = $input['uuid_usuario'] ?? null;
        $role = $input['role'] ?? 'emprendedor';

        if (!$uuid) {
            http_response_code(400);
            echo json_encode(['error' => 'uuid_usuario is required']);
            exit();
        }

        try {
            $projects = getProjectsByRole($pdo, $uuid, $role);
            echo json_encode(['projects' => $projects, 'count' => count($projects)]);
        } catch (Exception $e) {
            // Fallback strategy if column missing
            $stmt = $pdo->prepare("SELECT * FROM proyectos_negocio WHERE uuid_usuario = :uuid");
            $stmt->execute(['uuid' => $uuid]);
            $projects = $stmt->fetchAll();
            echo json_encode(['projects' => $projects, 'count' => count($projects), 'error' => 'RBAC_FALLBACK']);
        }
        break;

    case 'delete':
        if (!$projectId) {
            http_response_code(400);
            echo json_encode(['error' => 'id_proyecto is required for delete']);
            exit();
        }
        $stmt = $pdo->prepare("DELETE FROM proyectos_negocio WHERE id_proyecto = :id");
        $stmt->execute(['id' => $projectId]);
        echo json_encode(['success' => true, 'deleted' => $stmt->rowCount()]);
        break;

    default:
        http_response_code(400);
        echo json_encode(['error' => 'Unknown action. Use: create, update, get, list, delete']);
}
