<?php
declare(strict_types=1);

// 프론트 컨트롤러 (Apache/공유호스팅 + PHP 내장서버 공용).
// Apache 서브디렉터리(예: /powerPlus/) 배포를 고려해 경로 prefix는 무시하고
// 끝부분(/api/assets ...)으로 라우팅한다.
require_once __DIR__ . '/src/AssetController.php';
require_once __DIR__ . '/src/AuthController.php';
require_once __DIR__ . '/src/AuthService.php';
require_once __DIR__ . '/src/AdminController.php';
require_once __DIR__ . '/src/CategoryController.php';

// ── CORS (운영에서는 CORS_ORIGIN 으로 add-in 도메인만 허용) ──
$origin = getenv('CORS_ORIGIN') ?: '*';
header('Access-Control-Allow-Origin: ' . $origin);
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
$path   = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';
$path   = rtrim($path, '/');

/** JSON 응답 헬퍼 */
function json_out(mixed $payload, int $status = 200): void
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
}

/** 요청 본문(JSON) → 배열 */
function read_json_body(): array
{
    $raw  = file_get_contents('php://input') ?: '';
    $data = json_decode($raw, true);
    return is_array($data) ? $data : [];
}

/** Authorization: Bearer <token> 추출 (Apache/CGI 환경 차이 흡수) */
function bearer_token(): ?string
{
    $h = $_SERVER['HTTP_AUTHORIZATION'] ?? $_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? '';
    if ($h === '' && function_exists('apache_request_headers')) {
        $hdrs = apache_request_headers();
        $h = $hdrs['Authorization'] ?? $hdrs['authorization'] ?? '';
    }
    if (preg_match('/Bearer\s+(.+)/i', (string) $h, $m)) {
        return trim($m[1]);
    }
    return null;
}

// 헬스 체크
if (preg_match('#/health$#', $path)) {
    json_out(['status' => 'ok']);
    exit;
}

try {
    // ── 인증 라우트 (로그인 불필요) ──
    if (preg_match('#/api/auth/request$#', $path) && $method === 'POST') {
        (new AuthController())->request(read_json_body());
        exit;
    }
    if (preg_match('#/api/auth/verify$#', $path) && $method === 'POST') {
        (new AuthController())->verify(read_json_body());
        exit;
    }
    if (preg_match('#/api/auth/me$#', $path)) {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if ($email === null) {
            json_out(['error' => '인증이 필요합니다.', 'code' => 401], 401);
            exit;
        }
        json_out(['email' => $email, 'isAdmin' => AdminController::isAdmin($email)]);
        exit;
    }
    if (preg_match('#/api/auth/logout$#', $path) && $method === 'POST') {
        (new AuthController())->logout(bearer_token());
        exit;
    }

    // ── 카테고리 목록 (로그인 사용자) ──
    if (preg_match('#/api/categories$#', $path) && $method === 'GET') {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if ($email === null) {
            json_out(['error' => '인증이 필요합니다.', 'code' => 401], 401);
            exit;
        }
        (new CategoryController())->list();
        exit;
    }

    // ── 관리자 카테고리 CRUD (관리자만, JSON) ──
    if (preg_match('#/api/admin/categories(?:/([^/]+))?$#', $path, $m)) {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if (!AdminController::isAdmin($email)) {
            json_out(['error' => '관리자 권한이 필요합니다.', 'code' => 403], 403);
            exit;
        }
        $cc = new CategoryController();
        $key = $m[1] ?? '';
        if ($method === 'POST' && $key === '') {
            $cc->create(read_json_body());
            exit;
        }
        if ($method === 'PUT' && $key !== '') {
            $cc->update(urldecode($key), read_json_body());
            exit;
        }
        if ($method === 'DELETE' && $key !== '') {
            $cc->delete(urldecode($key));
            exit;
        }
        json_out(['error' => 'Not Found', 'code' => 404], 404);
        exit;
    }

    // ── 관리자 자산 CRUD (관리자만). 이미지 업로드 때문에 multipart(POST) 사용 ──
    if (preg_match('#/api/admin/assets(?:/([^/]+))?$#', $path, $m)) {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if (!AdminController::isAdmin($email)) {
            json_out(['error' => '관리자 권한이 필요합니다.', 'code' => 403], 403);
            exit;
        }
        $admin = new AdminController();
        $id = $m[1] ?? '';
        if ($method === 'POST' && $id === '') {
            $admin->create($_POST, $_FILES);           // 신규 (multipart)
            exit;
        }
        if ($method === 'POST' && $id !== '') {
            $admin->update(urldecode($id), $_POST, $_FILES); // 수정 (multipart)
            exit;
        }
        if ($method === 'DELETE' && $id !== '') {
            $admin->delete(urldecode($id));
            exit;
        }
        json_out(['error' => 'Not Found', 'code' => 404], 404);
        exit;
    }

    // ── 보호된 자산 라우트 (로그인 필요) ──
    if (preg_match('#/api/assets#', $path)) {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if ($email === null) {
            json_out(['error' => '인증이 필요합니다.', 'code' => 401], 401);
            exit;
        }
        $controller = new AssetController();
        if (preg_match('#/api/assets/([^/]+)$#', $path, $m)) {
            $controller->get(urldecode($m[1]));
            exit;
        }
        if (preg_match('#/api/assets$#', $path)) {
            $controller->list($_GET);
            exit;
        }
    }

    json_out(['error' => 'Not Found', 'code' => 404], 404);
} catch (Throwable $e) {
    // 운영에서는 상세 메시지 대신 logger로 기록할 것
    json_out(['error' => 'Internal Server Error', 'code' => 500], 500);
}
