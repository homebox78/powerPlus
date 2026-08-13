<?php
declare(strict_types=1);

require_once __DIR__ . '/Database.php';
require_once __DIR__ . '/Config.php';
require_once __DIR__ . '/SearchLexicon.php';

/** 자산 조회/검색/CRUD. SQL은 모두 prepared statement. */
final class AssetService
{
    // svg(구 mock 잔재, 실자산 전부 NULL)는 응답에서 제외 — raw SVG를 클라이언트에 내려보내지 않는다(stored-XSS 증폭 방지)
    private const COLS = 'id, name, category, tags, tags_ko, tags_en, image_path, thumb_path, slide_path, slide_kind, slide_page';

    /** 자산별 조회수(삽입 횟수) 및 즐겨찾기 수 서브쿼리 — 모든 응답에 노출(인기/즐겨찾기 순위용) */
    private const COUNT_COLS =
        '(SELECT COUNT(*) FROM usage_log u WHERE u.asset_id = a.id) AS views, ' .
        '(SELECT COUNT(*) FROM user_favorites f WHERE f.asset_id = a.id) AS fav_count';

    /** 정렬 키 → ORDER BY 절 (화이트리스트로 SQL 인젝션 방지) */
    private static function orderBy(string $sort): string
    {
        switch ($sort) {
            case 'popular':   // 인기순(뷰/삽입 많은 순)
                return 'ORDER BY views DESC, a.id';
            case 'favorites': // 즐겨찾기순(많이 즐겨찾기된 순)
                return 'ORDER BY fav_count DESC, a.id';
            case 'name':      // 이름순(이름 가나다, 없으면 뒤로)
                return 'ORDER BY (a.name IS NULL OR a.name = \'\'), a.name, a.id';
            case 'latest':    // 최신순(등록 시각 기준 — 카테고리 무관 최근 등록이 먼저, 없으면 id)
                return 'ORDER BY (a.created_at IS NULL), a.created_at DESC, a.id DESC';
            default:          // 기본(등록순 — 먼저 등록된 순)
                return 'ORDER BY a.id';
        }
    }

    /**
     * 카테고리 + 검색어(태그/이름) 필터 + 정렬 + 페이지네이션.
     * @return array{data:array<int,array>,total:int,page:int,limit:int}
     */
    public function list(string $category, string $q, int $page, int $limit, string $sort = 'latest', string $slideKind = '', string $slidePage = ''): array
    {
        $pdo = Database::pdo();
        $where = [];
        $whereParams = [];   // COUNT/WHERE 용(카테고리·장표 필터 등 기본 조건)
        $termParams  = [];   // 검색 낱말 조건
        $catParams   = [];   // 카테고리 제한 조건("사진·아이콘" 같은 종류 낱말)
        $scoreParams = [];   // 관련도 점수식 전용(SELECT 에서만 사용)
        if ($category !== '' && $category !== 'all') {
            $where[] = 'a.category = :category';
            $whereParams[':category'] = $category;
        }
        // 장표(ppt) 세부 필터: 유형(package/single) · 페이지 종류(cover/toc/divider/…)
        if ($slideKind !== '') {
            $where[] = 'a.slide_kind = :skind';
            $whereParams[':skind'] = $slideKind;
        }
        if ($slidePage !== '') {
            $where[] = 'a.slide_page = :spage';
            $whereParams[':spage'] = $slidePage;
        }

        // 자연어 질의: 토큰화 → 동의어/한↔영/색상 확장 → 가중 관련도 점수
        $scoreExpr = null;
        $corrected = [];     // 오타 교정 결과(원본 => 고친 말) — 화면 안내용
        $steps = [];         // 좁은 조건 → 넓은 조건 순서(첫 결과가 나오는 단계를 쓴다)
        $q = trim($q);
        if ($q !== '') {
            $tokens = SearchLexicon::tokenize($q);
            // 오타 교정("코ㅡㄷ"·"코그" → "코드") — 아는 낱말은 그대로 두고 모르는 것만 고친다
            [$tokens, $corrected] = SearchLexicon::correctTokens($tokens);
            $catHints = SearchLexicon::categoryHints($tokens);

            // 토큰마다 "동의어 묶음"을 따로 유지한다 — 묶음 안은 OR, 묶음끼리는 AND(아래).
            $groups = [];
            $scoreParts = [];
            $i = 0;
            foreach ($tokens as $tok) {
                // "사진·일러스트·장표"처럼 종류를 가리키는 낱말은 태그가 아니라 분류다.
                // 자산 태그에 "사진"이 들어있는 경우는 드물어서, 이걸 AND 조건에 넣으면 결과가 0에 가까워진다.
                // → 점수(가점)에는 반영하되, 조건은 아래 카테고리 제한으로 건다.
                $isCatWord = SearchLexicon::categoryHints([$tok]) !== [];
                $terms = [];
                foreach (SearchLexicon::expand($tok) as $t) {
                    $t = trim($t);
                    if ($t !== '' && !in_array($t, $terms, true)) $terms[] = $t;
                }
                $terms = array_slice($terms, 0, 12);
                // 한 글자 낱말은 부분일치를 끈다 — "말"이 "도움말·맺음말"에 걸려 엉뚱한 게 쏟아진다.
                $exactOnly = mb_strlen($tok) < 2;
                $groupOr = [];
                foreach ($terms as $t) {
                    // ⚠️ name/tags 가 NULL 이면 (col LIKE x) 가 NULL 이고, 그 NULL 이 덧셈 전체를 NULL 로 만든다.
                    //    이름 없는 자산(아이콘·사진·일러스트 대부분)이 점수 NULL → 정렬 맨 뒤로 밀렸던 원인.
                    $quoted = '%"' . $t . '"%';      // JSON 태그 정확 매칭
                    $b = ":b$i";
                    $scoreParams[$b] = $quoted;
                    if ($isCatWord) {
                        // 가점만 — 이름/태그에 그 낱말이 있으면 조금 더 위로
                        $scoreParams[":ca$i"] = '%' . $t . '%';
                        $scoreParts[] = "(COALESCE(a.name,'') LIKE :ca$i)*2 + (COALESCE(a.tags,'') LIKE $b)*2";
                        $i++;
                        continue;
                    }
                    if ($exactOnly) {
                        // ⚠️ 쓰지 않는 파라미터를 바인딩하면 PDO(EMULATE_PREPARES=false)가 거부한다 —
                        //    WHERE 에 실제로 들어가는 것만 whereParams 에 넣는다.
                        $termParams[":wb$i"] = $quoted;
                        $scoreParts[] = "(COALESCE(a.tags,'') LIKE $b)*4";
                        $groupOr[] = "COALESCE(a.tags,'') LIKE :wb$i";
                    } else {
                        $like = '%' . $t . '%';
                        $a = ":a$i"; $c = ":c$i";
                        $scoreParams[$a] = $like;    // name 부분일치(점수)
                        $scoreParams[$c] = $like;    // tags 부분일치(점수)
                        $termParams[":wd$i"] = $like;
                        $termParams[":we$i"] = $like;
                        $scoreParts[] = "(COALESCE(a.name,'') LIKE $a)*4 + (COALESCE(a.tags,'') LIKE $b)*3 + (COALESCE(a.tags,'') LIKE $c)*1";
                        $groupOr[] = "COALESCE(a.tags,'') LIKE :wd$i OR COALESCE(a.name,'') LIKE :we$i";
                    }
                    $i++;
                }
                if ($groupOr) $groups[] = '(' . implode(' OR ', $groupOr) . ')';
            }
            $j = 0;
            $catOr = [];
            foreach ($catHints as $ch) {
                $cs = ":cs$j"; $cw = ":cw$j";
                $scoreParams[$cs] = $ch;             // 카테고리 힌트 가점
                $catParams[$cw] = $ch;
                // 사용자가 "아이콘"처럼 종류를 짚어 말했으면 그 카테고리를 확실히 앞으로 올린다.
                $scoreParts[] = "(a.category = $cs)*8";
                $catOr[] = "a.category = $cw";
                $j++;
            }
            if ($groups || $catOr) {
                // 좁은 것부터 차례로 시도한다. 앞 단계에 결과가 있으면 거기서 멈춘다.
                //  ① 종류 + 낱말 전부   "기후 사진" = 사진 중에서 기후
                //  ② 낱말 전부          (그 종류엔 없을 때. 종류는 가점으로만 남아 위로 올라온다)
                //  ③ 낱말 하나라도      (그래도 없을 때)
                $catClause = $catOr ? '(' . implode(' OR ', $catOr) . ')' : null;
                $allWords  = $groups ? '(' . implode(' AND ', $groups) . ')' : null;
                if ($allWords !== null && $catClause !== null) {
                    $steps[] = ['sql' => "($allWords AND $catClause)", 'cat' => true];
                    $steps[] = ['sql' => $allWords, 'cat' => false];
                } elseif ($allWords !== null) {
                    $steps[] = ['sql' => $allWords, 'cat' => false];
                } elseif ($catClause !== null) {
                    $steps[] = ['sql' => $catClause, 'cat' => true];
                }
                $steps[] = ['sql' => '(' . implode(' OR ', array_merge($groups, $catOr)) . ')', 'cat' => true];
                $scoreExpr = $scoreParts ? '(' . implode(' + ', $scoreParts) . ')' : null;
            }
        }

        $baseParams = $whereParams;  // 기본 조건 파라미터(검색 낱말 붙이기 전)
        $mkWhere = static fn(?string $search) => ($search !== null && $search !== '')
            ? ($where ? ('WHERE ' . implode(' AND ', array_merge($where, [$search]))) : "WHERE $search")
            : ($where ? ('WHERE ' . implode(' AND ', $where)) : '');

        // 좁은 조건부터 차례로 세어 보고, 결과가 나오는 첫 단계를 쓴다.
        // ⚠️ 조건마다 실제로 쓰이는 파라미터만 바인딩해야 한다(EMULATE_PREPARES=false).
        $whereSql = $mkWhere(null);
        $total = 0;
        if ($steps) {
            $last = count($steps) - 1;
            foreach ($steps as $n => $step) {
                $sql    = $mkWhere($step['sql']);
                $params = array_merge($baseParams, $termParams, $step['cat'] ? $catParams : []);
                $st = $pdo->prepare("SELECT COUNT(*) FROM assets a $sql");
                $st->execute($params);
                $cnt = (int) $st->fetchColumn();
                if ($cnt > 0 || $n === $last) {
                    $whereSql = $sql; $whereParams = $params; $total = $cnt;
                    break;
                }
            }
        } else {
            $countStmt = $pdo->prepare("SELECT COUNT(*) FROM assets a $whereSql");
            $countStmt->execute($whereParams);
            $total = (int) $countStmt->fetchColumn();
        }

        $cols = preg_replace('/(^|,\s*)/', '$1a.', self::COLS); // 모든 컬럼에 a. 별칭
        $offset = ($page - 1) * $limit;
        // 검색어가 있으면 관련도 우선 정렬, 그다음 선택한 정렬을 타이브레이크로.
        $orderSql = $scoreExpr
            ? ('ORDER BY _score DESC, ' . substr(self::orderBy($sort), strlen('ORDER BY ')))
            : self::orderBy($sort);
        $scoreSel = $scoreExpr ? ", $scoreExpr AS _score" : '';
        $stmt = $pdo->prepare(
            "SELECT $cols, " . self::COUNT_COLS . "$scoreSel FROM assets a $whereSql "
            . $orderSql . ' LIMIT :limit OFFSET :offset'
        );
        foreach ($whereParams as $k => $v) $stmt->bindValue($k, $v);
        foreach ($scoreParams as $k => $v) $stmt->bindValue($k, $v);
        $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
        $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
        $stmt->execute();

        return [
            'data'      => array_map([$this, 'hydrate'], $stmt->fetchAll()),
            'total'     => $total,
            'page'      => $page,
            'limit'     => $limit,
            'corrected' => $corrected ?: null,
        ];
    }

    /**
     * 특정 id 목록의 자산만 조회 — 즐겨찾기/최근이 전체(수천 개)를 받아오지 않게.
     * 순서/정렬은 호출측(애드인)에서. @param array<int,string> $ids
     */
    public function byIds(array $ids): array
    {
        $ids = array_values(array_unique(array_filter(array_map('strval', $ids), static fn($s) => $s !== '')));
        $ids = array_slice($ids, 0, 1000);
        if (!$ids) {
            return ['data' => [], 'total' => 0];
        }
        $ph = [];
        $params = [];
        foreach ($ids as $k => $id) { $ph[] = ":id$k"; $params[":id$k"] = $id; }
        $cols = preg_replace('/(^|,\s*)/', '$1a.', self::COLS);
        $stmt = Database::pdo()->prepare(
            "SELECT $cols, " . self::COUNT_COLS . " FROM assets a WHERE a.id IN (" . implode(',', $ph) . ')'
        );
        $stmt->execute($params);
        return ['data' => array_map([$this, 'hydrate'], $stmt->fetchAll()), 'total' => count($ids)];
    }

    /**
     * 유사 자산 추천: 대상 자산의 태그를 공유하는 자산을 태그 중첩 수로 점수화.
     * 같은 카테고리 가점. 자기 자신 제외. (임베딩 도입 시 이 메서드를 벡터 검색으로 교체)
     */
    public function similar(string $id, int $limit = 12): array
    {
        $asset = $this->find($id);
        if ($asset === null) return ['data' => []];
        $tags = array_slice(array_values(array_unique($asset['tags'] ?? [])), 0, 16);
        $pdo = Database::pdo();

        $scoreParts = []; $orParts = [];
        $whereParams = [':self' => $id];
        $scoreParams = [];
        $i = 0;
        foreach ($tags as $t) {
            $t = trim((string) $t);
            if ($t === '') continue;
            $quoted = '%"' . $t . '"%';
            $s = ":s$i"; $w = ":w$i";
            $scoreParams[$s] = $quoted;
            $whereParams[$w] = $quoted;
            $scoreParts[] = "(COALESCE(a.tags,'') LIKE $s)*1";   // NULL 이면 점수 합이 통째로 NULL 이 된다
            $orParts[] = "COALESCE(a.tags,'') LIKE $w";
            $i++;
        }
        // 카테고리 가점(+ 태그가 없으면 같은 카테고리로 폴백)
        $scoreParams[':cats'] = $asset['category'];
        $scoreParts[] = "(a.category = :cats)*2";
        if (!$orParts) {
            $whereParams[':catw'] = $asset['category'];
            $orParts[] = 'a.category = :catw';
        }
        $scoreExpr = $scoreParts ? '(' . implode(' + ', $scoreParts) . ')' : '0';
        $whereOr = '(' . implode(' OR ', $orParts) . ')';

        $cols = preg_replace('/(^|,\s*)/', '$1a.', self::COLS);
        $stmt = $pdo->prepare(
            "SELECT $cols, " . self::COUNT_COLS . ", $scoreExpr AS _score
             FROM assets a
             WHERE a.id <> :self AND $whereOr
             ORDER BY _score DESC, views DESC, a.id
             LIMIT :limit"
        );
        foreach ($whereParams as $k => $v) $stmt->bindValue($k, $v);
        foreach ($scoreParams as $k => $v) $stmt->bindValue($k, $v);
        $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
        $stmt->execute();

        return ['data' => array_map([$this, 'hydrate'], $stmt->fetchAll())];
    }

    /**
     * 같은 스타일 세트(= 같은 등록 배치) 자산 목록.
     *
     * 아이콘 세트는 "한 번에 등록된 묶음"이 곧 같은 스타일이다(같은 소스·같은 태깅 파이프라인).
     * 그래서 created_at 이 30분 이내로 붙어 있는 자산들을 한 배치로 묶는다.
     * 재등록 1~2건짜리 자잘한 덩어리는 바로 앞 배치에 흡수(5건 미만).
     */
    public function styleSet(string $id, int $page = 1, int $limit = 60): array
    {
        $asset = $this->find($id);
        if ($asset === null) return ['data' => [], 'total' => 0, 'page' => 1, 'limit' => $limit];
        $pdo = Database::pdo();

        // 그 자산의 등록 시각
        $st = $pdo->prepare('SELECT created_at FROM assets WHERE id = :id');
        $st->execute([':id' => $id]);
        $at = $st->fetchColumn();
        if (!$at) return ['data' => [], 'total' => 0, 'page' => 1, 'limit' => $limit];

        // 같은 카테고리의 등록 시각 목록(시각별 개수)
        $st = $pdo->prepare(
            'SELECT created_at AS t, COUNT(*) AS n FROM assets
             WHERE category = :cat AND created_at IS NOT NULL
             GROUP BY created_at ORDER BY created_at'
        );
        $st->execute([':cat' => $asset['category']]);
        $rows = $st->fetchAll();

        $GAP = 30 * 60;   // 30분 이상 벌어지면 다른 배치
        $MIN = 5;         // 5건 미만 덩어리는 앞 배치에 흡수
        $clusters = [];   // [start, end, n]
        foreach ($rows as $r) {
            $t = strtotime((string) $r['t']);
            $n = (int) $r['n'];
            $last = $clusters ? $clusters[count($clusters) - 1] : null;
            if ($last !== null && $t - strtotime($last[1]) <= $GAP) {
                $clusters[count($clusters) - 1][1] = $r['t'];
                $clusters[count($clusters) - 1][2] += $n;
            } else {
                $clusters[] = [$r['t'], $r['t'], $n];
            }
        }
        // 작은 덩어리 흡수(앞 배치가 있을 때만)
        $merged = [];
        foreach ($clusters as $c) {
            if ($merged && $c[2] < $MIN) {
                $merged[count($merged) - 1][1] = $c[1];
                $merged[count($merged) - 1][2] += $c[2];
            } else {
                $merged[] = $c;
            }
        }

        // 대상 자산이 속한 배치 찾기
        $atTs = strtotime((string) $at);
        $range = null;
        foreach ($merged as $c) {
            if ($atTs >= strtotime($c[0]) && $atTs <= strtotime($c[1])) { $range = $c; break; }
        }
        if ($range === null) $range = [$at, $at, 1];

        $where = 'WHERE a.category = :cat AND a.created_at BETWEEN :s AND :e';
        $params = [':cat' => $asset['category'], ':s' => $range[0], ':e' => $range[1]];

        $st = $pdo->prepare("SELECT COUNT(*) FROM assets a $where");
        $st->execute($params);
        $total = (int) $st->fetchColumn();

        $page = max(1, $page);
        $offset = ($page - 1) * $limit;
        $cols = preg_replace('/(^|,\s*)/', '$1a.', self::COLS);
        // 대상 자산을 맨 앞에
        $st = $pdo->prepare(
            "SELECT $cols, " . self::COUNT_COLS . "
             FROM assets a $where
             ORDER BY (a.id = :self) DESC, a.id
             LIMIT :limit OFFSET :offset"
        );
        foreach ($params as $k => $v) $st->bindValue($k, $v);
        $st->bindValue(':self', $id);
        $st->bindValue(':limit', $limit, PDO::PARAM_INT);
        $st->bindValue(':offset', $offset, PDO::PARAM_INT);
        $st->execute();

        return [
            'data'  => array_map([$this, 'hydrate'], $st->fetchAll()),
            'total' => $total,
            'page'  => $page,
            'limit' => $limit,
        ];
    }

    public function find(string $id): ?array
    {
        $stmt = Database::pdo()->prepare('SELECT ' . self::COLS . ' FROM assets WHERE id = :id');
        $stmt->execute([':id' => $id]);
        $row = $stmt->fetch();
        return $row ? $this->hydrate($row) : null;
    }

    /** 카테고리별 다음 자동 ID 생성 (예: icon_001, icon_002 …). 화면엔 노출 안 함. */
    public function nextId(string $category): string
    {
        $stmt = Database::pdo()->prepare('SELECT id FROM assets WHERE category = :c');
        $stmt->execute([':c' => $category]);
        $max = 0;
        foreach ($stmt->fetchAll(PDO::FETCH_COLUMN) as $id) {
            if (preg_match('/(\d+)$/', (string) $id, $m)) {
                $max = max($max, (int) $m[1]);
            }
        }
        return $category . '_' . str_pad((string) ($max + 1), 3, '0', STR_PAD_LEFT);
    }

    /** 국문+영문 태그를 합쳐 검색용 통합 태그 배열 생성 */
    private static function mergeTags(array $ko, array $en): array
    {
        return array_values(array_unique(array_merge(array_values($ko), array_values($en))));
    }

    /** @param array{id:string,name?:?string,category:string,tags_ko?:array,tags_en?:array,svg?:?string,image_path?:?string,slide_path?:?string} $d */
    public function create(array $d): array
    {
        $ko = $d['tags_ko'] ?? [];
        $en = $d['tags_en'] ?? [];
        Database::pdo()->prepare(
            'INSERT INTO assets (id, name, category, tags, tags_ko, tags_en, svg, image_path, thumb_path, slide_path, slide_kind, slide_page, created_at)
             VALUES (:id, :name, :category, :tags, :tags_ko, :tags_en, :svg, :image_path, :thumb_path, :slide_path, :slide_kind, :slide_page, NOW())'
        )->execute([
            ':id'         => $d['id'],
            ':name'       => $d['name'] ?? null,
            ':category'   => $d['category'],
            ':tags'       => json_encode(self::mergeTags($ko, $en), JSON_UNESCAPED_UNICODE),
            ':tags_ko'    => json_encode(array_values($ko), JSON_UNESCAPED_UNICODE),
            ':tags_en'    => json_encode(array_values($en), JSON_UNESCAPED_UNICODE),
            ':svg'        => $d['svg'] ?? null,
            ':image_path' => $d['image_path'] ?? null,
            ':thumb_path' => $d['thumb_path'] ?? null,
            ':slide_path' => $d['slide_path'] ?? null,
            ':slide_kind' => $d['slide_kind'] ?? null,
            ':slide_page' => $d['slide_page'] ?? null,
        ]);
        return $this->find($d['id']) ?? [];
    }

    /** 부분 수정: 전달된 키만 갱신. */
    public function update(string $id, array $d): bool
    {
        $cur = $this->find($id);
        if ($cur === null) {
            return false;
        }
        $name       = array_key_exists('name', $d) ? $d['name'] : ($cur['name'] ?? null);
        $category   = $d['category'] ?? $cur['category'];
        $ko         = array_key_exists('tags_ko', $d) ? $d['tags_ko'] : ($cur['tags_ko'] ?? []);
        $en         = array_key_exists('tags_en', $d) ? $d['tags_en'] : ($cur['tags_en'] ?? []);
        $image_path = array_key_exists('image_path', $d) && $d['image_path'] !== null
            ? $d['image_path'] : ($cur['image_path'] ?? null);
        $slide_path = array_key_exists('slide_path', $d) && $d['slide_path'] !== null
            ? $d['slide_path'] : ($cur['slide_path'] ?? null);
        $thumb_path = array_key_exists('thumb_path', $d) && $d['thumb_path'] !== null
            ? $d['thumb_path'] : ($cur['thumb_path'] ?? null);
        $slide_kind = array_key_exists('slide_kind', $d) ? $d['slide_kind'] : ($cur['slide_kind'] ?? null);
        $slide_page = array_key_exists('slide_page', $d) ? $d['slide_page'] : ($cur['slide_page'] ?? null);

        Database::pdo()->prepare(
            'UPDATE assets SET name = :name, category = :category, tags = :tags, tags_ko = :tags_ko, tags_en = :tags_en, image_path = :image_path, thumb_path = :thumb_path, slide_path = :slide_path, slide_kind = :slide_kind, slide_page = :slide_page WHERE id = :id'
        )->execute([
            ':id'         => $id,
            ':name'       => $name,
            ':category'   => $category,
            ':tags'       => json_encode(self::mergeTags($ko, $en), JSON_UNESCAPED_UNICODE),
            ':tags_ko'    => json_encode(array_values($ko), JSON_UNESCAPED_UNICODE),
            ':tags_en'    => json_encode(array_values($en), JSON_UNESCAPED_UNICODE),
            ':image_path' => $image_path,
            ':thumb_path' => $thumb_path,
            ':slide_path' => $slide_path,
            ':slide_kind' => $slide_kind,
            ':slide_page' => $slide_page,
        ]);
        return true;
    }

    public function delete(string $id): bool
    {
        $stmt = Database::pdo()->prepare('DELETE FROM assets WHERE id = :id');
        $stmt->execute([':id' => $id]);
        return $stmt->rowCount() > 0;
    }

    /** tags(통합/ko/en) → 배열, image_path/thumb_path/slide_path → 전체 URL(image_url 등). */
    private function hydrate(array $row): array
    {
        unset($row['_score']); // 관련도 점수는 내부용 — 응답에서 제외
        // 인기/즐겨찾기 순위용 카운트 (list 쿼리에서만 존재)
        if (array_key_exists('views', $row)) {
            $row['views'] = (int) $row['views'];
        }
        if (array_key_exists('fav_count', $row)) {
            $row['fav_count'] = (int) $row['fav_count'];
        }
        $row['tags']    = json_decode((string) ($row['tags'] ?? '[]'), true) ?: [];
        $row['tags_ko'] = json_decode((string) ($row['tags_ko'] ?? '[]'), true) ?: [];
        $row['tags_en'] = json_decode((string) ($row['tags_en'] ?? '[]'), true) ?: [];
        // 구 자산(분리 태그 없음)은 통합 tags 를 국문 칸 기본값으로
        if (!$row['tags_ko'] && !$row['tags_en'] && $row['tags']) {
            $row['tags_ko'] = $row['tags'];
        }
        $base = rtrim((string) Config::get('public_base_url', 'https://hom2box.com/powerPlus'), '/');
        // 이미지 수정 시 같은 파일명이라 브라우저가 옛 이미지를 캐시 → 파일 수정시각을 ?v= 로 붙여 자동 갱신
        $root = __DIR__ . '/../';
        $ver = static function ($rel) use ($root) {
            $m = @filemtime($root . ltrim((string) $rel, '/'));
            return $m ? '?v=' . $m : '';
        };
        $row['image_url'] = !empty($row['image_path'])
            ? $base . '/' . ltrim((string) $row['image_path'], '/') . $ver($row['image_path'])
            : null;
        // 목록 표시용 썸네일 URL (없으면 원본으로 폴백). 삽입은 항상 image_url(원본) 사용.
        $row['thumb_url'] = !empty($row['thumb_path'])
            ? $base . '/' . ltrim((string) $row['thumb_path'], '/') . $ver($row['thumb_path'])
            : $row['image_url'];
        // 장표(ppt) 자산: 슬라이드 파일 URL (삽입 시 슬라이드로 추가)
        $row['slide_url'] = !empty($row['slide_path'])
            ? $base . '/' . ltrim((string) $row['slide_path'], '/')
            : null;
        return $row;
    }
}
