<?php
/**
 * API Endpoint: Ejecutar Agente de Investigación IA
 * Descripción: Debuggeable version.
 */

header('Content-Type: application/json');

// Permitir CORS local
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'error' => 'Método no permitido']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
$projectId = $input['id_proyecto'] ?? null;

if (!$projectId) {
    echo json_encode(['success' => false, 'error' => 'Falta ID del proyecto']);
    exit;
}

// Configuración
$pythonBin = "/usr/bin/python3";
$sitePackages = "/Users/robertoeduardocelisrobles/Library/Python/3.9/lib/python/site-packages";
$scriptPath = "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/PlanIA-CAFES/scripts/ai_research_agent.py";

// Paso 1: Verificar si Python existe y versión
$cmdVersion = "$pythonBin --version 2>&1";
exec($cmdVersion, $outVer, $retVer);

if ($retVer !== 0) {
    echo json_encode(['success' => false, 'error' => 'PHP no puede ejecutar Python', 'details' => implode("\n", $outVer)]);
    exit;
}

// Paso 2: Verificar si puede importar módulos (Ollama, MySQL) y Conectar a BD
// Nota: Ejecutamos un pequeño script inline para probar imports y conexión
$testCode = "
import sys
sys.path.append('$sitePackages')
try:
    import ollama
    import mysql.connector
    import selenium
    print('Imports OK')
except Exception as e:
    print('Import Error:', e)
    sys.exit(1)
";

$cmdTest = "$pythonBin -c " . escapeshellarg($testCode) . " 2>&1";
exec($cmdTest, $outTest, $retTest);

if ($retTest !== 0) {
    echo json_encode([
        'success' => false,
        'error' => 'Fallaron los imports o entorno Python',
        'details' => implode("\n", $outTest),
        'debug_cmd' => $cmdTest
    ]);
    exit;
}

// Paso 3: Ejecutar el script real
// Usamos PYTHONPATH explícito + -u para unbuffered
$command = "export PYTHONPATH=\$PYTHONPATH:" . escapeshellarg($sitePackages) . " && " .
    escapeshellarg($pythonBin) . " -u " . escapeshellarg($scriptPath) . " " . escapeshellarg($projectId) . " 2>&1";

exec($command, $output, $returnCode);

if ($returnCode === 0) {
    echo json_encode([
        'success' => true,
        'message' => 'Investigación completada exitosamente',
        'logs' => array_slice($output, -20)
    ]);
} else {
    echo json_encode([
        'success' => false,
        'error' => 'Error en script principal (Código ' . $returnCode . ')',
        'details' => implode("\n", $output),
        'debug_cmd' => $command
    ]);
}
?>