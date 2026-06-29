<?php
declare(strict_types=1);

require_once __DIR__ . '/AssetService.php';

/** HTTP 요청을 받아 JSON 응답을 내보내는 컨트롤러. */
final class AssetController
{
    private AssetService $service;

    public function __construct()
    {
        $this->service = new AssetService();
    }

    /** GET /api/assets?category=&q=&page=&limit= */
    public function list(array $query): void
    {
        $category = isset($query['category']) ? (string) $query['category'] : 'all';
        $q        = isset($query['q']) ? (string) $query['q'] : '';
        $page     = max(1, (int) ($query['page'] ?? 1));
        $limit    = (int) ($query['limit'] ?? 50);
        $limit    = max(1, min(2000, $limit ?: 50));
        $sort     = isset($query['sort']) ? (string) $query['sort'] : 'latest';
        $kind     = isset($query['kind']) ? (string) $query['kind'] : '';   // package|single
        $ptype    = isset($query['ptype']) ? (string) $query['ptype'] : ''; // cover|toc|divider|content|greeting|qa|etc

        $this->json($this->service->list($category, $q, $page, $limit, $sort, $kind, $ptype));
    }

    /** GET /api/assets/{id}/similar — 유사 자산 추천 */
    public function similar(string $id, array $query = []): void
    {
        $limit = max(1, min(50, (int) ($query['limit'] ?? 12)));
        $this->json($this->service->similar($id, $limit));
    }

    /** GET /api/assets/{id} */
    public function get(string $id): void
    {
        $asset = $this->service->find($id);
        if ($asset === null) {
            $this->json(['error' => '자산을 찾을 수 없습니다', 'code' => 404], 404);
            return;
        }
        $this->json(['data' => $asset]);
    }

    private function json(mixed $payload, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    }
}
