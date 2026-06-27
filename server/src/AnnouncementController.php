<?php
declare(strict_types=1);

require_once __DIR__ . '/AnnouncementService.php';

/** 공지(알람) HTTP 컨트롤러 — JSON 응답. */
final class AnnouncementController
{
    private AnnouncementService $service;

    public function __construct()
    {
        $this->service = new AnnouncementService();
    }

    /** GET /api/announcements (로그인 사용자) — 활성 공지만 */
    public function listActive(): void
    {
        $this->json(['data' => $this->service->listActive()]);
    }

    /** GET /api/admin/announcements (관리자) — 전체 */
    public function listAll(): void
    {
        $this->json(['data' => $this->service->listAll()]);
    }

    /** POST /api/admin/announcements (관리자, JSON) */
    public function create(array $body): void
    {
        $title = trim((string) ($body['title'] ?? ''));
        if ($title === '') {
            $this->json(['error' => '제목은 필수입니다.', 'code' => 400], 400);
            return;
        }
        $row = $this->service->create($title, (string) ($body['body'] ?? ''), (bool) ($body['is_active'] ?? true));
        $this->json(['data' => $row], 201);
    }

    /** PUT /api/admin/announcements/{id} (관리자, JSON) */
    public function update(int $id, array $body): void
    {
        $title = trim((string) ($body['title'] ?? ''));
        if ($title === '') {
            $this->json(['error' => '제목은 필수입니다.', 'code' => 400], 400);
            return;
        }
        $this->service->update($id, $title, (string) ($body['body'] ?? ''), (bool) ($body['is_active'] ?? true));
        $this->json(['ok' => true]);
    }

    /** DELETE /api/admin/announcements/{id} (관리자) */
    public function delete(int $id): void
    {
        $ok = $this->service->delete($id);
        $this->json(['ok' => $ok], $ok ? 200 : 404);
    }

    private function json(mixed $payload, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    }
}
