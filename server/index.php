<?php
declare(strict_types=1);

// 프론트 컨트롤러 (Apache/공유호스팅 + PHP 내장서버 공용).
// Apache 서브디렉터리(예: /powerPlus/) 배포를 고려해 경로 prefix는 무시하고
// 끝부분(/api/assets ...)으로 라우팅한다.
require_once __DIR__ . '/src/AssetController.php';

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

// 헬스 체크
if (preg_match('#/health$#', $path)) {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['status' => 'ok']);
    exit;
}

$controller = new AssetController();

try {
    if (preg_match('#/api/assets/([^/]+)$#', $path, $m)) {
        $controller->get(urldecode($m[1]));
        exit;
    }
    if (preg_match('#/api/assets$#', $path)) {
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
