<?php
header('Content-Type: text/plain');

try {
    // Hardcoded credentials for Docker environment
    $host = 'mysql-db';
    $db_name = 'osint_system';
    $user = 'root';
    $pass = 'root';

    $dsn = "mysql:host=$host;dbname=$db_name;charset=utf8mb4";
    $pdo = new PDO($dsn, $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
    ]);

    $sql = "CREATE TABLE IF NOT EXISTS ai_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        source VARCHAR(50) NOT NULL COMMENT 'web, telegram, whatsapp',
        user_id VARCHAR(100) DEFAULT NULL COMMENT 'Username or UUID',
        input_prompt TEXT,
        output_response MEDIUMTEXT,
        model_used VARCHAR(50),
        metadata JSON DEFAULT NULL,
        INDEX idx_source (source),
        INDEX idx_timestamp (timestamp)
    ) ENGINE=InnoDB;";

    $pdo->exec($sql);
    echo "SUCCESS: Table ai_logs created in $db_name (Host: $host)";

} catch (PDOException $e) {
    echo "ERROR: " . $e->getMessage();
}
?>