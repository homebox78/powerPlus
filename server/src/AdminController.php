<?php
declare(strict_types=1);

require_once __DIR__ . '/AssetService.php';
require_once __DIR__ . '/CategoryService.php';
require_once __DIR__ . '/Config.php';

/** 관리자용 자산 CRUD. 이미지는 PNG/JPG 파일 업로드, ID는 카테고리별 자동 생성. */
final class AdminController
{
    private const MAX_BYTES = 5 * 1024 * 1024; // 5MB
    private AssetService $service;
    private CategoryService $categories;

    public function __construct()
    {
        $this->service = new AssetService();
        $this->categories = new CategoryService();
    }

    public static function isAdmin(?string $email): bool
    {
        if ($email === null) {
            return false;
        }
        $admins = Config::get('admin_emails', []);
        $admins = is_array($admins) ? $admins : [];
        return in_array(strtolower($email), array_map('strtolower', $admins), true);
    }

    /** POST /api/admin/assets  (multipart: category, tags, name?, image=파일) */
    public function create(array $post, array $files): void
    {
        $category = trim((string) ($post['category'] ?? ''));
        if (!$this->categories->exists($category)) {
            $this->json(['error' => '존재하지 않는 카테고리입니다.', 'code' => 400], 400);
            return;
        }
        $ko = $this->parseTags($post['tags_ko'] ?? '');
        $en = $this->parseTags($post['tags_en'] ?? '');
        if (count($ko) + count($en) === 0) {
            $this->json(['error' => '태그(키워드)를 국문/영문 중 한쪽이라도 입력하세요.', 'code' => 400], 400);
            return;
        }
        $id = $this->service->nextId($category);
        $imagePath = $this->saveImage($files['image'] ?? null, $category, $id);
        if (isset($imagePath['error'])) {
            $this->json(['error' => $imagePath['error'], 'code' => 400], 400);
            return;
        }
        $asset = $this->service->create([
            'id'         => $id,
            'name'       => ($post['name'] ?? '') !== '' ? (string) $post['name'] : null,
            'category'   => $category,
            'tags_ko'    => $ko,
            'tags_en'    => $en,
            'image_path' => $imagePath['path'],
        ]);
        $this->json(['data' => $asset], 201);
    }

    /** POST /api/admin/assets/{id}  (multipart: category?, tags?, name?, image=파일(선택)) */
    public function update(string $id, array $post, array $files): void
    {
        if ($this->service->find($id) === null) {
            $this->json(['error' => '자산을 찾을 수 없습니다.', 'code' => 404], 404);
            return;
        }
        $patch = [];
        if (isset($post['category'])) {
            $category = trim((string) $post['category']);
            if (!$this->categories->exists($category)) {
                $this->json(['error' => '존재하지 않는 카테고리입니다.', 'code' => 400], 400);
                return;
            }
            $patch['category'] = $category;
        }
        if (isset($post['tags_ko']) || isset($post['tags_en'])) {
            $ko = $this->parseTags($post['tags_ko'] ?? '');
            $en = $this->parseTags($post['tags_en'] ?? '');
            if (count($ko) + count($en) === 0) {
                $this->json(['error' => '태그를 국문/영문 중 한쪽이라도 입력하세요.', 'code' => 400], 400);
                return;
            }
            $patch['tags_ko'] = $ko;
            $patch['tags_en'] = $en;
        }
        if (array_key_exists('name', $post)) {
            $patch['name'] = $post['name'] !== '' ? (string) $post['name'] : null;
        }
        // 새 이미지가 올라온 경우에만 교체
        if (isset($files['image']) && ($files['image']['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_NO_FILE) {
            $cat = $patch['category'] ?? (string) ($this->service->find($id)['category']);
            $saved = $this->saveImage($files['image'], $cat, $id);
            if (isset($saved['error'])) {
                $this->json(['error' => $saved['error'], 'code' => 400], 400);
                return;
            }
            $patch['image_path'] = $saved['path'];
        }
        $this->service->update($id, $patch);
        $this->json(['data' => $this->service->find($id)]);
    }

    /** DELETE /api/admin/assets/{id} */
    public function delete(string $id): void
    {
        $asset = $this->service->find($id);
        if ($asset === null) {
            $this->json(['error' => '자산을 찾을 수 없습니다.', 'code' => 404], 404);
            return;
        }
        if (!empty($asset['image_path'])) {
            @unlink(__DIR__ . '/../' . $asset['image_path']);
        }
        $this->service->delete($id);
        $this->json(['ok' => true]);
    }

    /** 업로드 파일 검증(PNG/JPG) 후 uploads/{category}/{id}.{ext} 로 저장. */
    private function saveImage(?array $file, string $category, string $id): array
    {
        if ($file === null || ($file['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK) {
            return ['error' => '이미지 파일을 올려주세요 (PNG 또는 JPG).'];
        }
        if (($file['size'] ?? 0) > self::MAX_BYTES) {
            return ['error' => '이미지가 너무 큽니다 (최대 5MB).'];
        }
        $finfo = finfo_open(FILEINFO_MIME_TYPE);
        $mime = finfo_file($finfo, $file['tmp_name']);
        finfo_close($finfo);
        $extByMime = ['image/png' => 'png', 'image/jpeg' => 'jpg'];
        if (!isset($extByMime[$mime])) {
            return ['error' => 'PNG 또는 JPG 파일만 업로드할 수 있습니다.'];
        }
        $ext = $extByMime[$mime];
        $dir = __DIR__ . '/../uploads/' . $category;
        if (!is_dir($dir) && !@mkdir($dir, 0775, true) && !is_dir($dir)) {
            return ['error' => '업로드 폴더를 만들 수 없습니다. (권한 확인)'];
        }
        $rel = "uploads/$category/$id.$ext";
        if (!@move_uploaded_file($file['tmp_name'], __DIR__ . '/../' . $rel)) {
            return ['error' => '파일 저장에 실패했습니다. (서버 권한 확인)'];
        }
        return ['path' => $rel];
    }

    /** tags: JSON 배열 문자열 또는 콤마 구분 문자열 → 배열(중복/공백 제거) */
    private function parseTags(mixed $raw): array
    {
        if (is_array($raw)) {
            $arr = $raw;
        } else {
            $s = (string) $raw;
            $decoded = json_decode($s, true);
            $arr = is_array($decoded) ? $decoded : explode(',', $s);
        }
        $arr = array_map(static fn($t) => trim((string) $t), $arr);
        $arr = array_values(array_unique(array_filter($arr, static fn($t) => $t !== '')));
        return $arr;
    }

    private function json(mixed $payload, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    }
}
