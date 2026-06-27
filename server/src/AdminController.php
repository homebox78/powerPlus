<?php
declare(strict_types=1);

require_once __DIR__ . '/AssetService.php';
require_once __DIR__ . '/Config.php';

/** 관리자용 자산 CRUD 엔드포인트. 라우터에서 관리자 권한 확인 후 호출된다. */
final class AdminController
{
    private AssetService $service;

    public function __construct()
    {
        $this->service = new AssetService();
    }

    /** 이메일이 관리자 목록에 있는지 */
    public static function isAdmin(?string $email): bool
    {
        if ($email === null) {
            return false;
        }
        $admins = Config::get('admin_emails', []);
        $admins = is_array($admins) ? $admins : [];
        return in_array(strtolower($email), array_map('strtolower', $admins), true);
    }

    /** POST /api/admin/assets */
    public function create(array $body): void
    {
        $data = $this->validate($body, true);
        if (isset($data['error'])) {
            $this->json(['error' => $data['error'], 'code' => 400], 400);
            return;
        }
        if ($this->service->find($data['id']) !== null) {
            $this->json(['error' => '이미 같은 ID의 자산이 있습니다.', 'code' => 409], 409);
            return;
        }
        $this->json(['data' => $this->service->create($data)], 201);
    }

    /** PUT /api/admin/assets/{id} */
    public function update(string $id, array $body): void
    {
        if ($this->service->find($id) === null) {
            $this->json(['error' => '자산을 찾을 수 없습니다.', 'code' => 404], 404);
            return;
        }
        $data = $this->validate($body, false);
        if (isset($data['error'])) {
            $this->json(['error' => $data['error'], 'code' => 400], 400);
            return;
        }
        $this->service->update($id, $data);
        $this->json(['data' => $this->service->find($id)]);
    }

    /** DELETE /api/admin/assets/{id} */
    public function delete(string $id): void
    {
        if (!$this->service->delete($id)) {
            $this->json(['error' => '자산을 찾을 수 없습니다.', 'code' => 404], 404);
            return;
        }
        $this->json(['ok' => true]);
    }

    /**
     * 입력 검증/정규화. tags 는 배열 또는 콤마 문자열 허용.
     * @return array{id?:string,name:string,category:string,tags:array,svg:string}|array{error:string}
     */
    private function validate(array $body, bool $requireId): array
    {
        $name     = trim((string) ($body['name'] ?? ''));
        $category = trim((string) ($body['category'] ?? ''));
        $svg      = trim((string) ($body['svg'] ?? ''));

        $allowed = ['icon', 'photo', 'illust', 'diagram'];
        if ($name === '' || $svg === '') {
            return ['error' => '이름과 SVG는 필수입니다.'];
        }
        if (!in_array($category, $allowed, true)) {
            return ['error' => '카테고리는 icon/photo/illust/diagram 중 하나여야 합니다.'];
        }
        if (stripos($svg, '<svg') === false) {
            return ['error' => 'SVG 형식이 올바르지 않습니다. (<svg ...> 필요)'];
        }

        // tags: 배열이면 그대로, 문자열이면 콤마 분리
        $rawTags = $body['tags'] ?? [];
        if (is_string($rawTags)) {
            $rawTags = array_filter(array_map('trim', explode(',', $rawTags)), fn($t) => $t !== '');
        }
        $tags = is_array($rawTags) ? array_values(array_map('strval', $rawTags)) : [];

        $out = ['name' => $name, 'category' => $category, 'tags' => $tags, 'svg' => $svg];

        if ($requireId) {
            $id = trim((string) ($body['id'] ?? ''));
            if (!preg_match('/^[a-z0-9][a-z0-9-]{1,63}$/i', $id)) {
                return ['error' => 'ID는 영문/숫자/하이픈 2~64자여야 합니다. (예: ic-heart)'];
            }
            $out['id'] = $id;
        }
        return $out;
    }

    private function json(mixed $payload, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    }
}
