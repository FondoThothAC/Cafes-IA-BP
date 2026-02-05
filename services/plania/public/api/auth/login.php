<?php
// API Endpoint for User Authentication
// public/api/auth/login.php

header('Content-Type: application/json');
require_once __DIR__ . '/../../../config/database.php';

// Allow CORS for local dev if needed
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
$username = $input['username'] ?? '';
$password = $input['password'] ?? '';

if (!$username || !$password) {
    echo json_encode(['success' => false, 'error' => 'Faltan credenciales']);
    exit;
}

try {
    // Database Connection
    // NOTE: Reusing existing config logic or environment vars
    $host = getenv('DB_HOST') ?: 'db';
    $db_name = getenv('DB_NAME') ?: 'plania';
    $user = getenv('DB_USER') ?: 'plania_user';
    $pass = getenv('DB_PASS') ?: 'plania_pass_2026';

    $dsn = "mysql:host=$host;dbname=$db_name;charset=utf8mb4";
    $pdo = new PDO($dsn, $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
    ]);

    // Fetch User
    $stmt = $pdo->prepare("SELECT id, username, password_hash, role, full_name FROM users WHERE username = ? AND is_active = 1");
    $stmt->execute([$username]);
    $userRow = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($userRow && verifyPassword($password, $userRow['password_hash'])) {
        // Success
        // Generate a simple Session Token (In prod use proper JWT)
        $sessionToken = bin2hex(random_bytes(32)); // Mock token

        // Log Session (Optional: could store in DB)

        echo json_encode([
            'success' => true,
            'session' => [
                'token' => $sessionToken,
                'user_id' => $userRow['id'],
                'username' => $userRow['username'],
                'role' => $userRow['role'],
                'full_name' => $userRow['full_name'],
                'login_at' => date('c')
            ]
        ]);
    } else {
        // Invalid
        http_response_code(401);
        echo json_encode(['success' => false, 'error' => 'Usuario o contraseña incorrectos']);
    }

} catch (PDOException $e) {
    // Fallback for Demo/Dev if DB is down (Auth Bypass for specific user if needed for testing UI)
    // REMOVE IN PRODUCTION
    if ($username === 'admin' && $password === 'admin123') {
        echo json_encode([
            'success' => true,
            'session' => [
                'token' => 'mock_token_admin_offline',
                'user_id' => 1,
                'username' => 'admin',
                'role' => 'admin',
                'full_name' => 'Admin Offline Mode',
                'login_at' => date('c')
            ]
        ]);
        exit;
    }

    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Error de conexión: ' . $e->getMessage()]);
}

// Helper password verify (handles simple hash for demo or bcrypt)
function verifyPassword($plain, $hash)
{
    // If hash starts with $, assume bcrypt/argon
    if (strpos($hash, '$') === 0) {
        return password_verify($plain, $hash);
    }
    // Fallback for simple cleartext/md5 (legacy support)
    return $plain === $hash;
}
?>