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

    /** 자산 총수 + 카테고리별 수 — 대시보드가 전체 자산을 로드하지 않고도 KPI/분포를 그리게. */
    public function assetCounts(): array
    {
        $by = [];
        foreach (Database::pdo()->query("SELECT category, COUNT(*) c FROM assets GROUP BY category") as $r) {
            $by[(string) $r['category']] = (int) $r['c'];
        }
        return ['total' => array_sum($by), 'byCategory' => $by];
    }

    /**
     * 시계열 통계 — 기간 버킷별 방문자수 / 삽입수 / 제안서(장표) 삽입수.
     * @param string $period 'day'|'month'|'year'
     * @return array{period:string,points:array<int,array{bucket:string,visits:int,inserts:int,ppt:int}>}
     */
    public function series(string $period = 'day', int $limit = 30): array
    {
        // 포맷은 화이트리스트로 결정(주입 불가)
        $fmt = $period === 'year' ? '%Y' : ($period === 'month' ? '%Y-%m' : '%Y-%m-%d');
        $limit = max(1, min(120, $limit));
        $pdo = Database::pdo();

        $map = static function (string $sql) use ($pdo): array {
            $out = [];
            foreach ($pdo->query($sql) as $r) {
                $out[(string) $r['b']] = (int) $r['c'];
            }
            return $out;
        };
        $visits  = $map("SELECT DATE_FORMAT(day, '$fmt') b, COUNT(DISTINCT email) c FROM visits GROUP BY b");
        $inserts = $map("SELECT DATE_FORMAT(used_at, '$fmt') b, COUNT(*) c FROM usage_log GROUP BY b");
        $ppt     = $map("SELECT DATE_FORMAT(u.used_at, '$fmt') b, COUNT(*) c FROM usage_log u JOIN assets a ON a.id = u.asset_id WHERE a.category='ppt' GROUP BY b");

        $buckets = array_keys($visits + $inserts + $ppt);
        sort($buckets);                       // 오래된→최신
        $buckets = array_slice($buckets, -$limit); // 최근 N개만

        $points = [];
        foreach ($buckets as $b) {
            $points[] = [
                'bucket'  => $b,
                'visits'  => $visits[$b]  ?? 0,
                'inserts' => $inserts[$b] ?? 0,
                'ppt'     => $ppt[$b]     ?? 0,
            ];
        }
        return ['period' => $period, 'points' => $points];
    }
}
