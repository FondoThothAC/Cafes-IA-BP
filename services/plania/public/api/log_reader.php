<?php
// API Endpoint to read AI logs
// Called by Dashboard (via CORS or direct access)
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
require_once __DIR__ . '/../config/database.php';

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

    // Fetch last 100 logs
    $stmt = $pdo->query("SELECT * FROM ai_logs ORDER BY timestamp DESC LIMIT 100");
    $logs = $stmt->fetchAll(PDO::FETCH_ASSOC);

    echo json_encode(['logs' => $logs]);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>