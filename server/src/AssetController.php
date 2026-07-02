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

    /** GET /api/assets?category=&q=&page=&limit=  또는  ?ids=a,b,c (즐겨찾기/최근) */
    public function list(array $query, ?string $email = null): void
    {
        // id 목록 조회 — 즐겨찾기/최근이 전체를 받지 않고 콕 집어서(빠름·정확)
        $idsRaw = isset($query['ids']) ? trim((string) $query['ids']) : '';
        if ($idsRaw !== '') {
            $this->json($this->service->byIds(explode(',', $idsRaw)));
            return;
        }
        $category = isset($query['category']) ? (string) $query['category'] : 'all';
        $q        = isset($query['q']) ? (string) $query['q'] : '';
        $page     = max(1, (int) ($query['page'] ?? 1));
        $limit    = (int) ($query['limit'] ?? 50);
        $limit    = max(1, min(2000, $limit ?: 50));
        $sort     = isset($query['sort']) ? (string) $query['sort'] : 'latest';
        $kind     = isset($query['kind']) ? (string) $query['kind'] : '';   // package|single
        $ptype    = isset($query['ptype']) ? (string) $query['ptype'] : ''; // cover|toc|divider|content|greeting|qa|etc

        $result = $this->service->list($category, $q, $page, $limit, $sort, $kind, $ptype);

        // 검색 로그(무결과율·수요 파악) — 1페이지만 기록(무한스크롤 중복 방지), 실패해도 응답은 정상
        if ($q !== '' && $page === 1) {
            try {
                Database::pdo()->prepare(
                    'INSERT INTO search_logs (email, query, category, results, searched_at)
                     VALUES (:e, :q, :c, :n, NOW())'
                )->execute([
                    ':e' => $email,
                    ':q' => mb_substr(trim($q), 0, 255),
                    ':c' => $category,
                    ':n' => (int) ($result['total'] ?? 0),
                ]);
            } catch (Throwable $e) { /* 로깅 실패는 무시 */ }
        }

        $this->json($result);
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
