<?php
declare(strict_types=1);

require_once __DIR__ . '/UsageService.php';

/** 사용 기록(로그인 사용자) / 통계(관리자). */
final class UsageController
{
    private UsageService $service;

    public function __construct()
    {
        $this->service = new UsageService();
    }

    /** POST /api/usage  { asset_id }  — 삽입 시 호출 */
    public function record(array $body, ?string $email): void
    {
        $assetId = trim((string) ($body['asset_id'] ?? ''));
        if ($assetId === '') {
            $this->json(['error' => 'asset_id 필요', 'code' => 400], 400);
            return;
        }
        $this->service->record($assetId, $email);
        $this->json(['ok' => true]);
    }

    /** GET /api/admin/stats — 많이 쓴 자산 통계 */
    public function stats(): void
    {
        $this->json([
            'summary' => $this->service->summary(),
            'top'     => $this->service->top(50),
        ]);
    }

    private function json(mixed $payload, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    }
}
