<?php
declare(strict_types=1);

require_once __DIR__ . '/Database.php';
require_once __DIR__ . '/AssetService.php';

/** 자산 사용(삽입) 기록 및 통계. */
final class UsageService
{
    public function record(string $assetId, ?string $email): void
    {
        Database::pdo()->prepare(
            'INSERT INTO usage_log (asset_id, email, used_at) VALUES (:a, :e, NOW())'
        )->execute([':a' => $assetId, ':e' => $email]);
    }

    /**
     * 뷰(삽입) 순위 — 많이 쓴 순 상위 자산 + 사용 횟수.
     * @return array<int,array{count:int,asset:?array}>
     */
    public function top(int $limit = 50): array
    {
        return $this->rank('usage_log', 'used_at', $limit);
    }

    /**
     * 즐겨찾기 순위 — 많이 즐겨찾기된 순 상위 자산 + 즐겨찾기 수.
     * @return array<int,array{count:int,asset:?array}>
     */
    public function topFavorites(int $limit = 50): array
    {
        return $this->rank('user_favorites', 'created_at', $limit);
    }

    /** 공통: 특정 테이블에서 asset_id 별 카운트 상위 N. */
    private function rank(string $table, string $dateCol, int $limit): array
    {
        $limit = max(1, min(200, $limit));
        $stmt = Database::pdo()->prepare(
            "SELECT asset_id, COUNT(*) AS cnt FROM $table
             GROUP BY asset_id ORDER BY cnt DESC, MAX($dateCol) DESC LIMIT :lim"
        );
        $stmt->bindValue(':lim', $limit, PDO::PARAM_INT);
        $stmt->execute();

        $assets = new AssetService();
        $out = [];
        foreach ($stmt->fetchAll() as $row) {
            $out[] = [
                'count' => (int) $row['cnt'],
                'asset' => $assets->find((string) $row['asset_id']),
            ];
        }
        return $out;
    }

    /** 전체 사용 횟수 / 고유 사용 자산 수 / 즐겨찾기 총 수 */
    public function summary(): array
    {
        $pdo = Database::pdo();
        return [
            'total'     => (int) $pdo->query('SELECT COUNT(*) FROM usage_log')->fetchColumn(),
            'unique'    => (int) $pdo->query('SELECT COUNT(DISTINCT asset_id) FROM usage_log')->fetchColumn(),
            'favorites' => (int) $pdo->query('SELECT COUNT(*) FROM user_favorites')->fetchColumn(),
        ];
    }
}
