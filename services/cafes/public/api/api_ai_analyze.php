<?php
/*
=================================================================================
PROYECTO: PlanIA - AI Analysis API
ARCHIVO: public/api/api_ai_analyze.php
COPYRIGHT: © 2026 Fondo Thoth AC.
LICENCIA: MIT
DESCRIPCIÓN: Endpoint para análisis de proyectos usando Ollama/Gemma3n
=================================================================================
*/

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Load environment variables
$envFile = __DIR__ . '/../../.env';
if (file_exists($envFile)) {
    $lines = file($envFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos($line, '#') === 0)
            continue;
        if (strpos($line, '=') !== false) {
            list($key, $value) = explode('=', $line, 2);
            $_ENV[trim($key)] = trim($value);
        }
    }
}

// Configuration
$OLLAMA_HOST = $_ENV['OLLAMA_HOST'] ?? 'http://localhost:11434';
$OLLAMA_MODEL = $_ENV['OLLAMA_MODEL'] ?? 'gemma3:4b-it';
$OLLAMA_TIMEOUT = intval($_ENV['OLLAMA_TIMEOUT'] ?? 120);

/**
 * Send a request to Ollama API
 */
function ollamaGenerate($prompt, $system = null, $images = null)
{
    global $OLLAMA_HOST, $OLLAMA_MODEL, $OLLAMA_TIMEOUT;

    $url = $OLLAMA_HOST . '/api/generate';

    $payload = [
        'model' => $OLLAMA_MODEL,
        'prompt' => $prompt,
        'stream' => false
    ];

    if ($system) {
        $payload['system'] = $system;
    }

    if ($images && is_array($images)) {
        $payload['images'] = $images;
    }

    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($payload),
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_TIMEOUT => $OLLAMA_TIMEOUT,
        CURLOPT_CONNECTTIMEOUT => 10
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    curl_close($ch);

    if ($error) {
        return ['error' => "Connection failed: $error"];
    }

    if ($httpCode !== 200) {
        return ['error' => "Ollama returned HTTP $httpCode"];
    }

    $data = json_decode($response, true);
    return ['response' => $data['response'] ?? ''];
}

// Main handler
try {
    $input = json_decode(file_get_contents('php://input'), true);

    if (!$input || !isset($input['action'])) {
        throw new Exception('Missing action parameter');
    }

    $action = $input['action'];
    $projectData = $input['data'] ?? [];

    switch ($action) {
        case 'analyze_project':
            $system = "Eres un Consultor Senior de Negocios experto en PYMES mexicanas.
                      Analiza proyectos de emprendimiento y proporciona recomendaciones prácticas.
                      Responde siempre en español de forma concisa.";

            $prompt = "Analiza este proyecto de negocio y proporciona:
                      1. Fortalezas identificadas
                      2. Áreas de mejora
                      3. 3 recomendaciones estratégicas específicas
                      
                      Datos del proyecto:
                      Nombre: " . ($projectData['a1_nombre_negocio'] ?? 'No especificado') . "
                      Descripción: " . ($projectData['b1_descripcion_negocio'] ?? 'No especificada') . "
                      Cliente objetivo: " . ($projectData['b4_cliente_objetivo_resumen'] ?? 'No especificado') . "
                      Propuesta de valor: " . ($projectData['b3_propuesta_valor'] ?? 'No especificada');

            $result = ollamaGenerate($prompt, $system);
            break;

        case 'analyze_market':
            $system = "Eres un analista de mercado especializado en México.
                      Proporciona análisis precisos basados en datos. Responde en español.";

            $prompt = "Realiza un análisis de mercado para este negocio:
                      Nombre: " . ($projectData['a1_nombre_negocio'] ?? 'No especificado') . "
                      Segmento: " . ($projectData['d1_segmento_cliente'] ?? 'No especificado') . "
                      Ventaja: " . ($projectData['d5_ventaja_competitiva'] ?? 'No especificada');

            $result = ollamaGenerate($prompt, $system);
            break;

        case 'analyze_image':
            if (empty($input['image'])) {
                throw new Exception('No image provided');
            }

            $system = "Eres un experto en branding y diseño visual para negocios.
                      Analiza imágenes y proporciona feedback constructivo. Responde en español.";

            $context = $input['context'] ?? '';
            $prompt = "Analiza esta imagen y proporciona:
                      1. Descripción de lo que ves
                      2. Fortalezas del diseño
                      3. Sugerencias de mejora
                      " . ($context ? "Contexto: $context" : "");

            $result = ollamaGenerate($prompt, $system, [$input['image']]);
            break;

        case 'generate_recommendations':
            $module = $input['module'] ?? 'general';
            $system = "Eres un consultor experto en $module para PYMES mexicanas.
                      Proporciona recomendaciones prácticas y accionables. Responde en español.";

            $prompt = "Proporciona 5 recomendaciones específicas para mejorar el área de $module:
                      
                      Negocio: " . ($projectData['a1_nombre_negocio'] ?? 'No especificado') . "
                      Descripción: " . ($projectData['b1_descripcion_negocio'] ?? 'No especificada');

            $result = ollamaGenerate($prompt, $system);
            break;

        case 'check_status':
            // Check if Ollama is available
            $ch = curl_init($OLLAMA_HOST . '/api/tags');
            curl_setopt_array($ch, [
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_TIMEOUT => 5
            ]);
            $response = curl_exec($ch);
            $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);

            if ($httpCode === 200) {
                $models = json_decode($response, true)['models'] ?? [];
                $result = [
                    'available' => true,
                    'host' => $OLLAMA_HOST,
                    'model' => $OLLAMA_MODEL,
                    'models_count' => count($models)
                ];
            } else {
                $result = ['available' => false, 'host' => $OLLAMA_HOST];
            }
            break;

        default:
            throw new Exception("Unknown action: $action");
    }

    if (isset($result['error'])) {
        echo json_encode(['success' => false, 'error' => $result['error']]);
    } else {
        echo json_encode([
            'success' => true,
            'analysis' => $result['response'] ?? null,
            'available' => $result['available'] ?? null,
            'host' => $result['host'] ?? null,
            'model' => $result['model'] ?? $OLLAMA_MODEL
        ]);
    }

} catch (Exception $e) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
}
