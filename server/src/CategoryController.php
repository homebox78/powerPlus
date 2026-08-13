<?php
declare(strict_types=1);

require_once __DIR__ . '/CategoryService.php';

/** 카테고리 CRUD. 목록(GET)은 로그인 사용자, 변경은 관리자(라우터에서 확인). */
final class CategoryController
{
    private CategoryService $service;

    public function __construct()
    {
        $this->service = new CategoryService();
    }

    /** GET /api/categories */
    public function list(): void
    {
        $this->json(['data' => $this->service->allWithCounts()]);
    }

    /** POST /api/admin/categories  { key, label, sort_order? } */
    public function create(array $body): void
    {
        $key   = strtolower(trim((string) ($body['key'] ?? '')));
        $label = trim((string) ($body['label'] ?? ''));
        $sort  = (int) ($body['sort_order'] ?? 0);

        if (!preg_match('/^[a-z0-9][a-z0-9-]{0,31}$/', $key)) {
            $this->json(['error' => 'key 는 영문소문자/숫자/하이픈 1~32자여야 합니다.', 'code' => 400], 400);
            return;
        }
        if ($label === '') {
            $this->json(['error' => '이름(label)은 필수입니다.', 'code' => 400], 400);
            return;
        }
        if ($this->service->exists($key)) {
            $this->json(['error' => '이미 있는 카테고리 key 입니다.', 'code' => 409], 409);
            return;
        }
        $this->service->create($key, $label, $sort);
        $this->json(['ok' => true], 201);
    }

    /** PUT /api/admin/categories/{key}  { label, sort_order? } */
    public function update(string $key, array $body): void
    {
        if (!$this->service->exists($key)) {
            $this->json(['error' => '카테고리를 찾을 수 없습니다.', 'code' => 404], 404);
            return;
        }
        $label = trim((string) ($body['label'] ?? ''));
        $sort  = (int) ($body['sort_order'] ?? 0);
        if ($label === '') {
            $this->json(['error' => '이름(label)은 필수입니다.', 'code' => 400], 400);
            return;
        }
        $this->service->update($key, $label, $sort);
        $this->json(['ok' => true]);
    }

    /** DELETE /api/admin/categories/{key} — 사용 중이면 막는다. */
    public function delete(string $key): void
    {
        if (!$this->service->exists($key)) {
            $this->json(['error' => '카테고리를 찾을 수 없습니다.', 'code' => 404], 404);
            return;
        }
        $count = $this->service->assetCount($key);
        if ($count > 0) {
            $this->json(['error' => "이 카테고리를 쓰는 자산이 {$count}개 있어 삭제할 수 없습니다. 먼저 자산을 옮기세요.", 'code' => 409], 409);
            return;
        }
        $this->service->delete($key);
        $this->json(['ok' => true]);
    }

    private function json(mixed $payload, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    }
}
