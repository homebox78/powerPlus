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

    /** GET /api/admin/stats — 요약/순위 + 자산 카운트(대시보드가 전체 자산 미로드로도 그리게) */
    public function stats(): void
    {
        $this->json([
            'summary'      => $this->service->summary(),
            'counts'       => $this->service->assetCounts(),
            'top'          => $this->service->top(50),
            'topFavorites' => $this->service->topFavorites(50),
        ]);
    }

    /** GET /api/admin/stats/series?period=day|month|year — 기간별 방문/삽입 추세 */
    public function series(): void
    {
        $period = $this->period();
        $limit = (int) ($_GET['limit'] ?? ($period === 'day' ? 30 : ($period === 'month' ? 24 : 8)));
        $this->json($this->service->series($period, $limit));
    }

    /** GET /api/admin/stats/analytics?period=day|month|year — 통계 탭 종합 분석 */
    public function analytics(): void
    {
        $period = $this->period();
        $limit = (int) ($_GET['limit'] ?? ($period === 'day' ? 30 : ($period === 'month' ? 24 : 8)));
        $this->json($this->service->analytics($period, $limit));
    }

    private function period(): string
    {
        $p = (string) ($_GET['period'] ?? 'day');
        return in_array($p, ['day', 'month', 'year'], true) ? $p : 'day';
    }

    private function json(mixed $payload, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    }
}
