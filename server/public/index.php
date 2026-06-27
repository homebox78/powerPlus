<?php
declare(strict_types=1);

require_once __DIR__ . '/../src/AssetController.php';

// ── CORS (운영에서는 CORS_ORIGIN 으로 add-in 도메인만 허용) ──
$origin = getenv('CORS_ORIGIN') ?: '*';
header('Access-Control-Allow-Origin: ' . $origin);
header('Access-Control-Allow-Methods: GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';
$path = rtrim($path, '/');
if ($path === '') {
    $path = '/';
}

// 헬스 체크
if ($path === '/health') {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['status' => 'ok']);
    exit;
}

$controller = new AssetController();

try {
    if (preg_match('#^/api/assets/([^/]+)$#', $path, $m)) {
        $controller->get(urldecode($m[1]));
        exit;
    }
    if ($path === '/api/assets') {
        $controller->list($_GET);
        exit;
    }

    http_response_code(404);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['error' => 'Not Found', 'code' => 404], JSON_UNESCAPED_UNICODE);
} catch (Throwable $e) {
    // 운영에서는 상세 메시지 대신 logger로 기록할 것
    http_response_code(500);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['error' => 'Internal Server Error', 'code' => 500], JSON_UNESCAPED_UNICODE);
}
