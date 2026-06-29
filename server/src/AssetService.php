<?php
declare(strict_types=1);

require_once __DIR__ . '/Database.php';
require_once __DIR__ . '/Config.php';
require_once __DIR__ . '/SearchLexicon.php';

/** 자산 조회/검색/CRUD. SQL은 모두 prepared statement. */
final class AssetService
{
    private const COLS = 'id, name, category, tags, tags_ko, tags_en, svg, image_path, thumb_path, slide_path, slide_kind, slide_page';

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
            default:          // 기본(등록 순)
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
        $whereParams = [];   // COUNT/WHERE 용
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
        $q = trim($q);
        if ($q !== '') {
            $tokens = SearchLexicon::tokenize($q);
            $terms = [];
            foreach ($tokens as $tok) {
                foreach (SearchLexicon::expand($tok) as $t) {
                    $t = trim($t);
                    if ($t !== '' && !in_array($t, $terms, true)) $terms[] = $t;
                }
            }
            $terms = array_slice($terms, 0, 24);
            $catHints = SearchLexicon::categoryHints($tokens);

            $scoreParts = [];
            $orParts = [];
            $i = 0;
            foreach ($terms as $t) {
                $like = '%' . $t . '%';
                $quoted = '%"' . $t . '"%';          // JSON 태그 거의-정확 매칭
                $a = ":a$i"; $b = ":b$i"; $c = ":c$i"; $d = ":d$i"; $e = ":e$i";
                $scoreParams[$a] = $like;            // name 부분일치(점수)
                $scoreParams[$b] = $quoted;          // tags 정확태그(점수)
                $scoreParams[$c] = $like;            // tags 부분일치(점수)
                $whereParams[$d] = $like;            // tags 부분일치(조건)
                $whereParams[$e] = $like;            // name 부분일치(조건)
                $scoreParts[] = "(a.name LIKE $a)*4 + (a.tags LIKE $b)*3 + (a.tags LIKE $c)*1";
                $orParts[] = "a.tags LIKE $d OR a.name LIKE $e";
                $i++;
            }
            $j = 0;
            foreach ($catHints as $ch) {
                $cs = ":cs$j"; $cw = ":cw$j";
                $scoreParams[$cs] = $ch;             // 카테고리 힌트 가점
                $whereParams[$cw] = $ch;             // 카테고리 힌트도 결과에 포함
                $scoreParts[] = "(a.category = $cs)*5";
                $orParts[] = "a.category = $cw";
                $j++;
            }
            if ($orParts) {
                $where[] = '(' . implode(' OR ', $orParts) . ')';
                $scoreExpr = '(' . implode(' + ', $scoreParts) . ')';
            }
        }

        $whereSql = $where ? ('WHERE ' . implode(' AND ', $where)) : '';

        $countStmt = $pdo->prepare("SELECT COUNT(*) FROM assets a $whereSql");
        $countStmt->execute($whereParams);
        $total = (int) $countStmt->fetchColumn();

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
            'data'  => array_map([$this, 'hydrate'], $stmt->fetchAll()),
            'total' => $total,
            'page'  => $page,
            'limit' => $limit,
        ];
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
            $scoreParts[] = "(a.tags LIKE $s)*1";
            $orParts[] = "a.tags LIKE $w";
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
            'INSERT INTO assets (id, name, category, tags, tags_ko, tags_en, svg, image_path, thumb_path, slide_path, slide_kind, slide_page)
             VALUES (:id, :name, :category, :tags, :tags_ko, :tags_en, :svg, :image_path, :thumb_path, :slide_path, :slide_kind, :slide_page)'
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

    /** tags(통합/ko/en) → 배열, image_path → 전체 URL(image_url). svg(구 mock)도 그대로 유지. */
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
