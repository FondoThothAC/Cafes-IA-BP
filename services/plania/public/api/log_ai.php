<?php
// API Endpoint to log AI interactions
// Called by API Gateway via internal network
header('Content-Type: application/json');
require_once __DIR__ . '/../config/database.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);

if (!$input) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON']);
    exit;
}

try {
    // Connect to DB (using env vars from docker-compose)
    $host = getenv('DB_HOST') ?: 'db';
    $db_name = getenv('DB_NAME') ?: 'plania';
    $user = getenv('DB_USER') ?: 'plania_user';
    $pass = getenv('DB_PASS') ?: 'plania_pass_2026';

    $dsn = "mysql:host=$host;dbname=$db_name;charset=utf8mb4";
    $pdo = new PDO($dsn, $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
    ]);

    $stmt = $pdo->prepare("INSERT INTO ai_logs (source, user_id, input_prompt, output_response, model_used, metadata) VALUES (?, ?, ?, ?, ?, ?)");

    $stmt->execute([
        $input['source'] ?? 'unknown',
        $input['user_id'] ?? 'anonymous',
        $input['prompt'] ?? '',
        $input['response'] ?? '',
        $input['model'] ?? '',
        json_encode($input['metadata'] ?? [])
    ]);

    echo json_encode(['success' => true, 'id' => $pdo->lastInsertId()]);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>