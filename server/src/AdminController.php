<?php
declare(strict_types=1);

require_once __DIR__ . '/AssetService.php';
require_once __DIR__ . '/CategoryService.php';
require_once __DIR__ . '/Config.php';
require_once __DIR__ . '/Thumb.php';

/** 관리자용 자산 CRUD. 이미지는 PNG/JPG 파일 업로드, ID는 카테고리별 자동 생성. */
final class AdminController
{
    private const MAX_BYTES = 5 * 1024 * 1024;        // 이미지 5MB
    private const MAX_SLIDE_BYTES = 40 * 1024 * 1024; // 장표(ppt/pptx) 40MB
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
        $data = [
            'id'       => $id,
            'name'     => ($post['name'] ?? '') !== '' ? (string) $post['name'] : null,
            'category' => $category,
            'tags_ko'  => $ko,
            'tags_en'  => $en,
        ];

        if ($category === 'ppt') {
            // 장표: .ppt/.pptx 파일 필수(slide_path), 썸네일 이미지(image_path)는 선택
            $slide = $this->saveSlide($files['slide'] ?? null, $id);
            if (isset($slide['error'])) {
                $this->json(['error' => $slide['error'], 'code' => 400], 400);
                return;
            }
            $data['slide_path'] = $slide['path'];
            // 세분화: 유형(package/single) + 페이지 종류(single일 때만)
            $kind = ($post['slide_kind'] ?? '') === 'single' ? 'single' : 'package';
            $data['slide_kind'] = $kind;
            $data['slide_page'] = $kind === 'single' ? (($post['slide_page'] ?? '') ?: 'etc') : null;
            if ($this->hasUpload($files['image'] ?? null)) {
                $img = $this->saveImage($files['image'], $category, $id);
                if (isset($img['error'])) {
                    $this->json(['error' => $img['error'], 'code' => 400], 400);
                    return;
                }
                $data['image_path'] = $img['path'];
                $data['thumb_path'] = $img['thumb'] ?? null;
            }
        } else {
            $img = $this->saveImage($files['image'] ?? null, $category, $id);
            if (isset($img['error'])) {
                $this->json(['error' => $img['error'], 'code' => 400], 400);
                return;
            }
            $data['image_path'] = $img['path'];
            $data['thumb_path'] = $img['thumb'] ?? null;
        }

        $asset = $this->service->create($data);
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
        if (isset($post['slide_kind'])) {
            $kind = $post['slide_kind'] === 'single' ? 'single' : 'package';
            $patch['slide_kind'] = $kind;
            $patch['slide_page'] = $kind === 'single' ? (($post['slide_page'] ?? '') ?: 'etc') : null;
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
        $cat = $patch['category'] ?? (string) ($this->service->find($id)['category']);
        // 새 이미지(썸네일)가 올라온 경우에만 교체
        if ($this->hasUpload($files['image'] ?? null)) {
            $saved = $this->saveImage($files['image'], $cat, $id);
            if (isset($saved['error'])) {
                $this->json(['error' => $saved['error'], 'code' => 400], 400);
                return;
            }
            $patch['image_path'] = $saved['path'];
            $patch['thumb_path'] = $saved['thumb'] ?? null;
        }
        // 장표 파일(.ppt/.pptx)이 올라온 경우에만 교체
        if ($this->hasUpload($files['slide'] ?? null)) {
            $saved = $this->saveSlide($files['slide'], $id);
            if (isset($saved['error'])) {
                $this->json(['error' => $saved['error'], 'code' => 400], 400);
                return;
            }
            $patch['slide_path'] = $saved['path'];
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
        if (!empty($asset['thumb_path'])) {
            @unlink(__DIR__ . '/../' . $asset['thumb_path']);
        }
        if (!empty($asset['slide_path'])) {
            @unlink(__DIR__ . '/../' . $asset['slide_path']);
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
        $absRoot = __DIR__ . '/../';
        if (!@move_uploaded_file($file['tmp_name'], $absRoot . $rel)) {
            return ['error' => '파일 저장에 실패했습니다. (서버 권한 확인)'];
        }
        // 목록 표시용 썸네일 생성 (실패해도 원본으로 폴백되므로 치명적 아님)
        $thumbRel = Thumb::pathFor($rel);
        $thumb = Thumb::make($absRoot . $rel, $absRoot . $thumbRel, 360) ? $thumbRel : null;
        return ['path' => $rel, 'thumb' => $thumb];
    }

    /** 업로드 파일이 실제로 존재하는지(선택 필드 판별). */
    private function hasUpload(?array $file): bool
    {
        return $file !== null && ($file['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_NO_FILE;
    }

    /** 장표 파일(.ppt/.pptx) 검증 후 uploads/ppt/{id}.{ext} 로 저장. */
    private function saveSlide(?array $file, string $id): array
    {
        if ($file === null || ($file['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK) {
            return ['error' => '장표 파일(.ppt 또는 .pptx)을 올려주세요.'];
        }
        if (($file['size'] ?? 0) > self::MAX_SLIDE_BYTES) {
            return ['error' => '장표 파일이 너무 큽니다 (최대 40MB).'];
        }
        // Office 파일은 finfo mime가 불안정(pptx=zip 등) → 확장자로 검증(관리자 전용)
        $ext = strtolower((string) pathinfo((string) ($file['name'] ?? ''), PATHINFO_EXTENSION));
        if (!in_array($ext, ['ppt', 'pptx'], true)) {
            return ['error' => '.ppt 또는 .pptx 파일만 업로드할 수 있습니다.'];
        }
        $dir = __DIR__ . '/../uploads/ppt';
        if (!is_dir($dir) && !@mkdir($dir, 0775, true) && !is_dir($dir)) {
            return ['error' => '업로드 폴더를 만들 수 없습니다. (권한 확인)'];
        }
        $rel = "uploads/ppt/$id.$ext";
        if (!@move_uploaded_file($file['tmp_name'], __DIR__ . '/../' . $rel)) {
            return ['error' => '장표 파일 저장에 실패했습니다. (서버 권한 확인)'];
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
