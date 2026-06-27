<?php
declare(strict_types=1);

require_once __DIR__ . '/PrefsService.php';

/** 로그인 사용자 본인의 즐겨찾기/최근. 라우터에서 토큰→email 검증 후 호출. */
final class PrefsController
{
    private PrefsService $service;

    public function __construct()
    {
        $this->service = new PrefsService();
    }

    /** GET /api/me/favorites */
    public function favorites(string $email): void
    {
        $this->json(['data' => $this->service->favorites($email)]);
    }

    /** POST /api/me/favorites  { asset_id } */
    public function addFavorite(string $email, array $body): void
    {
        $id = trim((string) ($body['asset_id'] ?? ''));
        if ($id === '') {
            $this->json(['error' => 'asset_id 가 필요합니다.', 'code' => 400], 400);
            return;
        }
        $this->service->addFavorite($email, $id);
        $this->json(['ok' => true]);
    }

    /** DELETE /api/me/favorites/{id} */
    public function removeFavorite(string $email, string $id): void
    {
        $this->service->removeFavorite($email, $id);
        $this->json(['ok' => true]);
    }

    /** GET /api/me/recent */
    public function recent(string $email): void
    {
        $this->json(['data' => $this->service->recent($email, 20)]);
    }

    private function json(mixed $payload, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    }
}
