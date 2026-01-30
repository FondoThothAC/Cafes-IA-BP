<?php
/**
 * =================================================================================
 * PROYECTO: PlanIA (Backend API)
 * ARCHIVO: public/upload_file.php
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: GPLv2
 * DESCRIPCIÓN: File upload endpoint for logos and images (local storage)
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

// Configuration
$UPLOAD_DIR = __DIR__ . '/uploads/';
$MAX_FILE_SIZE = 2 * 1024 * 1024; // 2MB
$ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml', 'image/webp'];
$ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'];

// Create upload directory if it doesn't exist
if (!file_exists($UPLOAD_DIR)) {
    mkdir($UPLOAD_DIR, 0755, true);
}

// Ensure logos subdirectory exists
$LOGOS_DIR = $UPLOAD_DIR . 'logos/';
if (!file_exists($LOGOS_DIR)) {
    mkdir($LOGOS_DIR, 0755, true);
}

// Check request method
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed. Use POST.']);
    exit();
}

// Check if file was uploaded
if (!isset($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
    $errorMessage = 'No file uploaded';
    if (isset($_FILES['file']['error'])) {
        switch ($_FILES['file']['error']) {
            case UPLOAD_ERR_INI_SIZE:
            case UPLOAD_ERR_FORM_SIZE:
                $errorMessage = 'File too large';
                break;
            case UPLOAD_ERR_NO_FILE:
                $errorMessage = 'No file selected';
                break;
            default:
                $errorMessage = 'Upload error: ' . $_FILES['file']['error'];
        }
    }
    http_response_code(400);
    echo json_encode(['error' => $errorMessage]);
    exit();
}

$file = $_FILES['file'];

// Validate file size
if ($file['size'] > $MAX_FILE_SIZE) {
    http_response_code(400);
    echo json_encode(['error' => 'File too large. Maximum size is 2MB.']);
    exit();
}

// Validate file type
$finfo = new finfo(FILEINFO_MIME_TYPE);
$mimeType = $finfo->file($file['tmp_name']);

if (!in_array($mimeType, $ALLOWED_TYPES)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid file type. Allowed: JPG, PNG, GIF, SVG, WebP.']);
    exit();
}

// Validate extension
$extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
if (!in_array($extension, $ALLOWED_EXTENSIONS)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid file extension.']);
    exit();
}

// Get upload type (logo, evidence, etc.)
$uploadType = $_POST['type'] ?? 'logo';
$projectId = $_POST['project_id'] ?? 'general';

// Generate unique filename
$timestamp = time();
$randomString = bin2hex(random_bytes(4));
$newFilename = "{$uploadType}_{$projectId}_{$timestamp}_{$randomString}.{$extension}";

// Determine target directory
$targetDir = $LOGOS_DIR;
if ($uploadType === 'evidence') {
    $evidenceDir = $UPLOAD_DIR . 'evidences/';
    if (!file_exists($evidenceDir)) {
        mkdir($evidenceDir, 0755, true);
    }
    $targetDir = $evidenceDir;
}

$targetPath = $targetDir . $newFilename;

// Move uploaded file
if (!move_uploaded_file($file['tmp_name'], $targetPath)) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to save file.']);
    exit();
}

// Generate URL (relative to public folder)
$relativePath = str_replace(__DIR__ . '/', '', $targetPath);
$fileUrl = $relativePath;

// Return success response
echo json_encode([
    'success' => true,
    'url' => $fileUrl,
    'filename' => $newFilename,
    'size' => $file['size'],
    'type' => $mimeType
]);
