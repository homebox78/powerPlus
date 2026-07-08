<?php
declare(strict_types=1);

// 운영: 에러 메시지를 화면에 노출하지 않음(정보 노출 방지). 로그로만 기록.
ini_set('display_errors', '0');
ini_set('log_errors', '1');

// 프론트 컨트롤러 (Apache/공유호스팅 + PHP 내장서버 공용).
// Apache 서브디렉터리(예: /powerPlus/) 배포를 고려해 경로 prefix는 무시하고
// 끝부분(/api/assets ...)으로 라우팅한다.
require_once __DIR__ . '/src/AssetController.php';
require_once __DIR__ . '/src/AuthController.php';
require_once __DIR__ . '/src/AuthService.php';
require_once __DIR__ . '/src/AdminController.php';
require_once __DIR__ . '/src/CategoryController.php';
require_once __DIR__ . '/src/UsageController.php';
require_once __DIR__ . '/src/PrefsController.php';
require_once __DIR__ . '/src/AnnouncementController.php';
require_once __DIR__ . '/src/RequestController.php';
require_once __DIR__ . '/src/ImageSearchController.php';

// ── CORS: 알려진 출처만 허용 (운영 도메인 + 로컬 dev). 그 외엔 운영 도메인으로 고정 ──
$allowedOrigins = array_filter([
    'https://hom2box.com',
    'https://localhost:3000',
    getenv('CORS_ORIGIN') ?: null,
]);
$reqOrigin = $_SERVER['HTTP_ORIGIN'] ?? '';
$origin = in_array($reqOrigin, $allowedOrigins, true) ? $reqOrigin : 'https://hom2box.com';
header('Access-Control-Allow-Origin: ' . $origin);
header('Vary: Origin');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
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
    // ── 공개 자산 목록/카테고리 (인증 불필요, 읽기 전용) — DeckGen 등 내부 도구 연동용 ──
    // 이미지(image_url/thumb_url)는 이미 공개 정적 파일이라 메타데이터 공개도 안전. 쓰기·삭제는 불가.
    if (preg_match('#/api/public/assets$#', $path) && $method === 'GET') {
        (new AssetController())->list($_GET, null);
        exit;
    }
    if (preg_match('#/api/public/assets/([^/]+)/similar$#', $path, $m) && $method === 'GET') {
        (new AssetController())->similar(urldecode($m[1]), $_GET);
        exit;
    }
    if (preg_match('#/api/public/categories$#', $path) && $method === 'GET') {
        (new CategoryController())->list();
        exit;
    }

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

    // ── 내 즐겨찾기 / 최근 (로그인 사용자 본인) ──
    if (preg_match('#/api/me/(favorites|recent)(?:/([^/]+))?$#', $path, $m)) {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if ($email === null) {
            json_out(['error' => '인증이 필요합니다.', 'code' => 401], 401);
            exit;
        }
        $pc = new PrefsController();
        $sub = $m[1];
        $id = $m[2] ?? '';
        if ($sub === 'favorites' && $method === 'GET' && $id === '') {
            $pc->favorites($email);
            exit;
        }
        if ($sub === 'favorites' && $method === 'POST' && $id === '') {
            $pc->addFavorite($email, read_json_body());
            exit;
        }
        if ($sub === 'favorites' && $method === 'DELETE' && $id !== '') {
            $pc->removeFavorite($email, urldecode($id));
            exit;
        }
        if ($sub === 'recent' && $method === 'GET') {
            $pc->recent($email);
            exit;
        }
        json_out(['error' => 'Not Found', 'code' => 404], 404);
        exit;
    }

    // ── 사용 기록 (로그인 사용자) — 삽입 시 호출 ──
    if (preg_match('#/api/usage$#', $path) && $method === 'POST') {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if ($email === null) {
            json_out(['error' => '인증이 필요합니다.', 'code' => 401], 401);
            exit;
        }
        (new UsageController())->record(read_json_body(), $email);
        exit;
    }

    // ── 무료 이미지 검색(Openverse) + 이미지 중계 (로그인 사용자) ──
    if (preg_match('#/api/imagesearch$#', $path) && $method === 'GET') {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if ($email === null) { json_out(['error' => '인증이 필요합니다.', 'code' => 401], 401); exit; }
        (new ImageSearchController())->search($_GET);
        exit;
    }
    if (preg_match('#/api/imageproxy$#', $path) && $method === 'GET') {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if ($email === null) { http_response_code(401); echo '인증이 필요합니다.'; exit; }
        (new ImageSearchController())->proxy($_GET);
        exit;
    }

    // ── 사용 통계 (관리자만) ──
    if (preg_match('#/api/admin/stats/series$#', $path) && $method === 'GET') {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if (!AdminController::isAdmin($email)) {
            json_out(['error' => '관리자 권한이 필요합니다.', 'code' => 403], 403);
            exit;
        }
        (new UsageController())->series();
        exit;
    }
    if (preg_match('#/api/admin/stats/analytics$#', $path) && $method === 'GET') {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if (!AdminController::isAdmin($email)) {
            json_out(['error' => '관리자 권한이 필요합니다.', 'code' => 403], 403);
            exit;
        }
        (new UsageController())->analytics();
        exit;
    }
    if (preg_match('#/api/admin/stats$#', $path) && $method === 'GET') {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if (!AdminController::isAdmin($email)) {
            json_out(['error' => '관리자 권한이 필요합니다.', 'code' => 403], 403);
            exit;
        }
        (new UsageController())->stats();
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

    // ── 콘텐츠 요청 등록 (로그인 사용자) ──
    if (preg_match('#/api/requests$#', $path) && $method === 'POST') {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if ($email === null) {
            json_out(['error' => '인증이 필요합니다.', 'code' => 401], 401);
            exit;
        }
        (new RequestController())->create(read_json_body(), $email);
        exit;
    }

    // ── 관리자 콘텐츠 요청 (관리자만) ──
    if (preg_match('#/api/admin/requests(?:/(\d+))?$#', $path, $m)) {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if (!AdminController::isAdmin($email)) {
            json_out(['error' => '관리자 권한이 필요합니다.', 'code' => 403], 403);
            exit;
        }
        $rc = new RequestController();
        $id = isset($m[1]) ? (int) $m[1] : 0;
        if ($method === 'GET' && $id === 0) {
            $rc->listAll();
            exit;
        }
        if ($method === 'PUT' && $id > 0) {
            $rc->update($id, read_json_body());
            exit;
        }
        if ($method === 'DELETE' && $id > 0) {
            $rc->delete($id);
            exit;
        }
        json_out(['error' => 'Not Found', 'code' => 404], 404);
        exit;
    }

    // ── 공지(알람) 목록 (로그인 사용자) — 활성 공지만 ──
    if (preg_match('#/api/announcements$#', $path) && $method === 'GET') {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if ($email === null) {
            json_out(['error' => '인증이 필요합니다.', 'code' => 401], 401);
            exit;
        }
        (new AnnouncementController())->listActive();
        exit;
    }

    // ── 관리자 공지 CRUD (관리자만, JSON) ──
    if (preg_match('#/api/admin/announcements(?:/(\d+))?$#', $path, $m)) {
        $email = (new AuthService())->validateToken(bearer_token() ?? '');
        if (!AdminController::isAdmin($email)) {
            json_out(['error' => '관리자 권한이 필요합니다.', 'code' => 403], 403);
            exit;
        }
        $ac = new AnnouncementController();
        $id = isset($m[1]) ? (int) $m[1] : 0;
        if ($method === 'GET' && $id === 0) {
            $ac->listAll();
            exit;
        }
        if ($method === 'POST' && $id === 0) {
            $ac->create(read_json_body());
            exit;
        }
        if ($method === 'PUT' && $id > 0) {
            $ac->update($id, read_json_body());
            exit;
        }
        if ($method === 'DELETE' && $id > 0) {
            $ac->delete($id);
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
        if (preg_match('#/api/assets/([^/]+)/similar$#', $path, $m)) {
            $controller->similar(urldecode($m[1]), $_GET);
            exit;
        }
        if (preg_match('#/api/assets/([^/]+)$#', $path, $m)) {
            $controller->get(urldecode($m[1]));
            exit;
        }
        if (preg_match('#/api/assets$#', $path)) {
            $controller->list($_GET, $email);
            exit;
        }
    }

    json_out(['error' => 'Not Found', 'code' => 404], 404);
} catch (Throwable $e) {
    // 운영에서는 상세 메시지 대신 logger로 기록할 것
    json_out(['error' => 'Internal Server Error', 'code' => 500], 500);
}
