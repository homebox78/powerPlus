<?php
declare(strict_types=1);

require_once __DIR__ . '/RequestService.php';

/** 콘텐츠 요청 HTTP 컨트롤러. */
final class RequestController
{
    private RequestService $service;

    public function __construct()
    {
        $this->service = new RequestService();
    }

    /** POST /api/requests (로그인 사용자) */
    public function create(array $body, ?string $email): void
    {
        $title = trim((string) ($body['title'] ?? ''));
        if ($title === '') {
            $this->json(['error' => '제목은 필수입니다.', 'code' => 400], 400);
            return;
        }
        // 참고 링크는 http(s)만 허용 — javascript: 등 스킴이 관리자 화면의 <a href>로 렌더되는 stored-XSS 차단
        $link = trim((string) ($body['link'] ?? ''));
        if ($link !== '' && (!preg_match('#^https?://#i', $link) || filter_var($link, FILTER_VALIDATE_URL) === false)) {
            $link = '';
        }
        $row = $this->service->create(
            $email,
            (string) ($body['type'] ?? '기타'),
            $title,
            (string) ($body['description'] ?? ''),
            $link
        );
        $this->json(['data' => $row], 201);
    }

    /** GET /api/admin/requests (관리자) */
    public function listAll(): void
    {
        $this->json(['data' => $this->service->listAll()]);
    }

    /** PUT /api/admin/requests/{id} (관리자) — 상태 변경 */
    public function update(int $id, array $body): void
    {
        $status = (string) ($body['status'] ?? 'new');
        if (!in_array($status, ['new', 'done', 'rejected'], true)) {
            $this->json(['error' => '잘못된 상태', 'code' => 400], 400);
            return;
        }
        $this->service->setStatus($id, $status);
        $this->json(['ok' => true]);
    }

    /** DELETE /api/admin/requests/{id} (관리자) */
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
