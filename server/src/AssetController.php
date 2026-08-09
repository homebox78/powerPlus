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

    /** GET /api/assets?category=&q=&page=&limit=  또는  ?ids=a,b,c (즐겨찾기/최근)
     *  $public=true(무인증 /api/public/*)면: limit 상한 축소 + 대외비 필드(slide_url 등) 제거 + 검색 로그 미기록 */
    public function list(array $query, ?string $email = null, bool $public = false): void
    {
        // id 목록 조회 — 즐겨찾기/최근이 전체를 받지 않고 콕 집어서(빠름·정확)
        $idsRaw = isset($query['ids']) ? trim((string) $query['ids']) : '';
        if ($idsRaw !== '') {
            $r = $this->service->byIds(explode(',', $idsRaw));
            if ($public) $r['data'] = array_map([self::class, 'stripPrivate'], $r['data']);
            $this->json($r);
            return;
        }
        $category = isset($query['category']) ? (string) $query['category'] : 'all';
        $q        = isset($query['q']) ? (string) $query['q'] : '';
        $page     = max(1, (int) ($query['page'] ?? 1));
        $limit    = (int) ($query['limit'] ?? 50);
        // 공개 라우트는 상한 축소 — 행마다 카운트 서브쿼리·filemtime이 붙어 무인증 대량 요청이 부하 벡터가 됨
        $limit    = max(1, min($public ? 200 : 2000, $limit ?: 50));
        $sort     = isset($query['sort']) ? (string) $query['sort'] : 'latest';
        $kind     = isset($query['kind']) ? (string) $query['kind'] : '';   // package|single
        $ptype    = isset($query['ptype']) ? (string) $query['ptype'] : ''; // cover|toc|divider|content|greeting|qa|etc

        $result = $this->service->list($category, $q, $page, $limit, $sort, $kind, $ptype);
        if ($public) $result['data'] = array_map([self::class, 'stripPrivate'], $result['data']);

        // 검색 로그(무결과율·수요 파악) — 로그인 사용자 1페이지만 기록(무한스크롤 중복·봇 트래픽의 지표 오염 방지)
        if ($q !== '' && $page === 1 && $email !== null) {
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
    public function similar(string $id, array $query = [], bool $public = false): void
    {
        $limit = max(1, min(50, (int) ($query['limit'] ?? 12)));
        $r = $this->service->similar($id, $limit);
        if ($public) $r['data'] = array_map([self::class, 'stripPrivate'], $r['data']);
        $this->json($r);
    }

    /** 공개(무인증) 응답에서 대외비 필드 제거.
     *  이미지(썸네일·원본)는 이미 공개 정적 파일이지만, 장표 원본(.pptx = 회사 제안서 분할본)의
     *  직링크(slide_url)까지 무인증 열거되면 안 되므로 공개 응답에선 뺀다. */
    private static function stripPrivate(array $asset): array
    {
        unset($asset['slide_url'], $asset['slide_path']);
        return $asset;
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
