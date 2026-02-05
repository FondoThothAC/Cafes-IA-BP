<?php
// scripts/test_db_users.php
require_once __DIR__ . '/../config/database.php';

try {
    $stmt = $pdo->query("SELECT id, username, role FROM users");
    $users = $stmt->fetchAll(PDO::FETCH_ASSOC);
    echo "Successfully connected! Found users:\n";
    print_r($users);
} catch (Exception $e) {
    echo "Error: " . $e->getMessage();
}
