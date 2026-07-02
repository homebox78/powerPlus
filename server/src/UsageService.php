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

    /**
     * 최근 삽입 내역 — 누가(email) · 무엇을(asset) · 언제(used_at). 최신순.
     * @return array<int,array{email:string,used_at:string,asset:?array}>
     */
    public function recentInserts(int $limit = 20): array
    {
        $limit = max(1, min(100, $limit));
        $stmt = Database::pdo()->prepare(
            'SELECT email, asset_id, used_at FROM usage_log ORDER BY id DESC LIMIT :lim'
        );
        $stmt->bindValue(':lim', $limit, PDO::PARAM_INT);
        $stmt->execute();

        $assets = new AssetService();
        $out = [];
        foreach ($stmt->fetchAll() as $row) {
            $out[] = [
                'email'   => (string) ($row['email'] ?? ''),
                'used_at' => (string) $row['used_at'],
                'asset'   => $assets->find((string) $row['asset_id']),
            ];
        }
        return $out;
    }

    /** 공통: 특정 테이블에서 asset_id 별 카운트 상위 N. */
    private function rank(string $table, string $dateCol, int $limit): array
    {
        $limit = max(1, min(200, $limit));
        // JOIN assets: 삭제된 자산(삽입/즐겨찾기 기록만 남고 실물 없는 것)은 순위에서 제외 → 빈 줄 방지
        $stmt = Database::pdo()->prepare(
            "SELECT t.asset_id, COUNT(*) AS cnt FROM $table t
             JOIN assets a ON a.id = t.asset_id
             GROUP BY t.asset_id ORDER BY cnt DESC, MAX(t.$dateCol) DESC LIMIT :lim"
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

    /**
     * 통계 탭용 종합 분석 — 추이(방문/삽입/제안서/즐겨찾기) + 카테고리별 사용 + 요일/시간대 + TOP 사용자/자산 + 총계.
     */
    public function analytics(string $period = 'day', int $limit = 30): array
    {
        $fmt = $period === 'year' ? '%Y' : ($period === 'month' ? '%Y-%m' : '%Y-%m-%d');
        $limit = max(1, min(120, $limit));
        $pdo = Database::pdo();
        $map = static function (string $sql) use ($pdo): array {
            $out = [];
            foreach ($pdo->query($sql) as $r) { $out[(string) $r['b']] = (int) $r['c']; }
            return $out;
        };

        // ── 시계열(버킷별) ──
        $visits  = $map("SELECT DATE_FORMAT(day, '$fmt') b, COUNT(DISTINCT email) c FROM visits GROUP BY b");
        $inserts = $map("SELECT DATE_FORMAT(used_at, '$fmt') b, COUNT(*) c FROM usage_log GROUP BY b");
        $ppt     = $map("SELECT DATE_FORMAT(u.used_at, '$fmt') b, COUNT(*) c FROM usage_log u JOIN assets a ON a.id=u.asset_id WHERE a.category='ppt' GROUP BY b");
        $favs    = $map("SELECT DATE_FORMAT(created_at, '$fmt') b, COUNT(*) c FROM user_favorites GROUP BY b");
        $buckets = array_keys($visits + $inserts + $ppt + $favs);
        sort($buckets);
        $buckets = array_slice($buckets, -$limit);
        $series = array_map(static fn($b) => [
            'bucket'    => $b,
            'visits'    => $visits[$b]  ?? 0,
            'inserts'   => $inserts[$b] ?? 0,
            'ppt'       => $ppt[$b]     ?? 0,
            'favorites' => $favs[$b]    ?? 0,
        ], $buckets);

        // ── 카테고리별 사용량(등록 수가 아니라 실제 삽입) ──
        $categoryUsage = [];
        foreach ($pdo->query("SELECT a.category cat, COUNT(*) c FROM usage_log u JOIN assets a ON a.id=u.asset_id GROUP BY a.category ORDER BY c DESC") as $r) {
            $categoryUsage[] = ['category' => (string) $r['cat'], 'count' => (int) $r['c']];
        }

        // ── 요일별(1=일~7=토) / 시간대별(0~23) 사용 패턴 ──
        $dowRaw = $map("SELECT DAYOFWEEK(used_at) b, COUNT(*) c FROM usage_log GROUP BY b");
        $dow = [];
        for ($i = 1; $i <= 7; $i++) { $dow[] = ['dow' => $i, 'count' => $dowRaw[(string) $i] ?? 0]; }
        $hourRaw = $map("SELECT HOUR(used_at) b, COUNT(*) c FROM usage_log GROUP BY b");
        $hour = [];
        for ($i = 0; $i < 24; $i++) { $hour[] = ['hour' => $i, 'count' => $hourRaw[(string) $i] ?? 0]; }

        // ── 활발한 사용자 TOP ──
        $topUsers = [];
        foreach ($pdo->query("SELECT email, COUNT(*) c FROM usage_log WHERE email IS NOT NULL AND email<>'' GROUP BY email ORDER BY c DESC LIMIT 10") as $r) {
            $topUsers[] = ['email' => (string) $r['email'], 'count' => (int) $r['c']];
        }

        // ── 총계 ──
        $totals = [
            'inserts'        => (int) $pdo->query("SELECT COUNT(*) FROM usage_log")->fetchColumn(),
            'favorites'      => (int) $pdo->query("SELECT COUNT(*) FROM user_favorites")->fetchColumn(),
            'visits'         => (int) $pdo->query("SELECT COUNT(*) FROM visits")->fetchColumn(),
            'uniqueVisitors' => (int) $pdo->query("SELECT COUNT(DISTINCT email) FROM visits")->fetchColumn(),
            'activeUsers'    => (int) $pdo->query("SELECT COUNT(DISTINCT email) FROM usage_log WHERE email IS NOT NULL AND email<>''")->fetchColumn(),
            'visitDays'      => (int) $pdo->query("SELECT COUNT(DISTINCT day) FROM visits")->fetchColumn(),
        ];

        // ── KPI (모니터링 핵심지표) ──
        $q = static fn(string $sql): int => (int) Database::pdo()->query($sql)->fetchColumn();
        $dau = $q("SELECT COUNT(DISTINCT email) FROM visits WHERE day = CURDATE()");
        $wau = $q("SELECT COUNT(DISTINCT email) FROM visits WHERE day >= CURDATE() - INTERVAL 6 DAY");
        $mau = $q("SELECT COUNT(DISTINCT email) FROM visits WHERE day >= CURDATE() - INTERVAL 29 DAY");
        $insToday = $q("SELECT COUNT(*) FROM usage_log WHERE DATE(used_at) = CURDATE()");
        $insYday  = $q("SELECT COUNT(*) FROM usage_log WHERE DATE(used_at) = CURDATE() - INTERVAL 1 DAY");
        $ins7     = $q("SELECT COUNT(*) FROM usage_log WHERE used_at >= CURDATE() - INTERVAL 6 DAY");
        $ins7prev = $q("SELECT COUNT(*) FROM usage_log WHERE used_at >= CURDATE() - INTERVAL 13 DAY AND used_at < CURDATE() - INTERVAL 6 DAY");
        $usedAssets  = $q("SELECT COUNT(DISTINCT u.asset_id) FROM usage_log u JOIN assets a ON a.id = u.asset_id");
        $totalAssets = $q("SELECT COUNT(*) FROM assets");
        $kpi = [
            'dau' => $dau, 'wau' => $wau, 'mau' => $mau,
            'insToday' => $insToday, 'insYesterday' => $insYday,
            'ins7d' => $ins7, 'ins7dPrev' => $ins7prev,
            'stickiness'    => $mau > 0 ? (int) round($dau / $mau * 100) : 0,
            'coverageUsed'  => $usedAssets,
            'coverageTotal' => $totalAssets,
            'coveragePct'   => $totalAssets > 0 ? (int) round($usedAssets / $totalAssets * 100) : 0,
        ];

        // ── 누적 성장(누적 삽입 · 누적 자산) — 전 구간 러닝합 후 표시구간만 ──
        $assetsPer = $map("SELECT DATE_FORMAT(created_at, '$fmt') b, COUNT(*) c FROM assets WHERE created_at IS NOT NULL GROUP BY b");
        $allB = array_keys($inserts + $assetsPer);
        sort($allB);
        $runIns = 0; $runAsset = 0; $cumMap = [];
        foreach ($allB as $b) {
            $runIns   += $inserts[$b]   ?? 0;
            $runAsset += $assetsPer[$b] ?? 0;
            $cumMap[$b] = ['inserts' => $runIns, 'assets' => $runAsset];
        }
        $cumulative = array_map(static fn($b) => [
            'bucket'  => $b,
            'inserts' => $cumMap[$b]['inserts'] ?? 0,
            'assets'  => $cumMap[$b]['assets']  ?? 0,
        ], $buckets);

        // ── 요일(0=일~6=토) × 시간(0~23) 히트맵: 삽입 밀도 ──
        $dhRaw = [];
        foreach ($pdo->query("SELECT DAYOFWEEK(used_at) d, HOUR(used_at) h, COUNT(*) c FROM usage_log GROUP BY d, h") as $r) {
            $dhRaw[((int) $r['d'] - 1) . '_' . (int) $r['h']] = (int) $r['c'];
        }
        $dowHour = [];
        for ($d = 0; $d < 7; $d++) {
            $rowc = [];
            for ($h = 0; $h < 24; $h++) { $rowc[] = $dhRaw[$d . '_' . $h] ?? 0; }
            $dowHour[] = $rowc;
        }

        // ── 카테고리별 커버리지(사용된 자산 / 등록 수) ──
        $cvTotal = [];
        foreach ($pdo->query("SELECT category cat, COUNT(*) c FROM assets GROUP BY category") as $r) { $cvTotal[(string) $r['cat']] = (int) $r['c']; }
        $cvUsed = [];
        foreach ($pdo->query("SELECT a.category cat, COUNT(DISTINCT u.asset_id) c FROM usage_log u JOIN assets a ON a.id = u.asset_id GROUP BY a.category") as $r) { $cvUsed[(string) $r['cat']] = (int) $r['c']; }
        $coverageByCat = [];
        foreach ($cvTotal as $cat => $tot) {
            $coverageByCat[] = ['category' => $cat, 'total' => $tot, 'used' => $cvUsed[$cat] ?? 0];
        }

        // ── 미충족 수요(콘텐츠 요청) — 테이블 없으면 무시 ──
        $requests = ['new' => 0, 'done' => 0, 'rejected' => 0, 'total' => 0];
        try {
            foreach ($pdo->query("SELECT status, COUNT(*) c FROM content_requests GROUP BY status") as $r) {
                $s = (string) $r['status'];
                if (isset($requests[$s])) { $requests[$s] = (int) $r['c']; }
                $requests['total'] += (int) $r['c'];
            }
        } catch (\Throwable $e) { /* content_requests 없음 */ }

        return [
            'period'        => $period,
            'series'        => $series,
            'cumulative'    => $cumulative,
            'categoryUsage' => $categoryUsage,
            'coverageByCat' => $coverageByCat,
            'dow'           => $dow,
            'hour'          => $hour,
            'dowHour'       => $dowHour,
            'topUsers'      => $topUsers,
            'topAssets'     => $this->top(10),
            'topFavorites'  => $this->topFavorites(10),
            'recentInserts' => $this->recentInserts(60),
            'requests'      => $requests,
            'kpi'           => $kpi,
            'totals'        => $totals,
            'search'        => $this->searchStats(30),
        ];
    }

    /** 검색 품질 통계(최근 N일) — 검색 수·무결과율·인기/무결과 검색어 TOP. 테이블 없으면 0. */
    private function searchStats(int $days = 30): array
    {
        $out = ['total' => 0, 'zero' => 0, 'zeroRate' => 0.0, 'top' => [], 'topZero' => []];
        try {
            $pdo = Database::pdo();
            $stmt = $pdo->prepare(
                "SELECT COUNT(*) t, SUM(results = 0) z FROM search_logs
                 WHERE searched_at >= DATE_SUB(NOW(), INTERVAL :d DAY)"
            );
            $stmt->execute([':d' => $days]);
            $row = $stmt->fetch();
            $out['total'] = (int) ($row['t'] ?? 0);
            $out['zero']  = (int) ($row['z'] ?? 0);
            $out['zeroRate'] = $out['total'] > 0 ? round($out['zero'] * 100 / $out['total'], 1) : 0.0;

            $q1 = $pdo->prepare(
                "SELECT query q, COUNT(*) n, SUM(results = 0) z FROM search_logs
                 WHERE searched_at >= DATE_SUB(NOW(), INTERVAL :d DAY)
                 GROUP BY query ORDER BY n DESC LIMIT 10"
            );
            $q1->execute([':d' => $days]);
            foreach ($q1 as $r) {
                $out['top'][] = ['q' => (string) $r['q'], 'n' => (int) $r['n'], 'zero' => (int) $r['z']];
            }

            $q2 = $pdo->prepare(
                "SELECT query q, COUNT(*) n FROM search_logs
                 WHERE results = 0 AND searched_at >= DATE_SUB(NOW(), INTERVAL :d DAY)
                 GROUP BY query ORDER BY n DESC LIMIT 10"
            );
            $q2->execute([':d' => $days]);
            foreach ($q2 as $r) {
                $out['topZero'][] = ['q' => (string) $r['q'], 'n' => (int) $r['n']];
            }
        } catch (\Throwable $e) { /* search_logs 미생성 등 — 0으로 */ }
        return $out;
    }
}
