<?php
declare(strict_types=1);

require_once __DIR__ . '/Database.php';
require_once __DIR__ . '/Config.php';

/** 자산 조회/검색/CRUD. SQL은 모두 prepared statement. */
final class AssetService
{
    private const COLS = 'id, name, category, tags, tags_ko, tags_en, svg, image_path';

    /**
     * 카테고리 + 검색어(태그/이름) 필터 + 페이지네이션.
     * @return array{data:array<int,array>,total:int,page:int,limit:int}
     */
    public function list(string $category, string $q, int $page, int $limit): array
    {
        $pdo = Database::pdo();
        $where = [];
        $params = [];
        if ($category !== '' && $category !== 'all') {
            $where[] = 'category = :category';
            $params[':category'] = $category;
        }
        $q = trim($q);
        if ($q !== '') {
            // 태그(JSON 텍스트) 또는 이름 부분일치
            $where[] = '(tags LIKE :q OR name LIKE :q)';
            $params[':q'] = '%' . $q . '%';
        }
        $whereSql = $where ? ('WHERE ' . implode(' AND ', $where)) : '';

        $countStmt = $pdo->prepare("SELECT COUNT(*) FROM assets $whereSql");
        $countStmt->execute($params);
        $total = (int) $countStmt->fetchColumn();

        $offset = ($page - 1) * $limit;
        $stmt = $pdo->prepare(
            'SELECT ' . self::COLS . " FROM assets $whereSql ORDER BY id LIMIT :limit OFFSET :offset"
        );
        foreach ($params as $k => $v) {
            $stmt->bindValue($k, $v);
        }
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

    /** @param array{id:string,name?:?string,category:string,tags_ko?:array,tags_en?:array,svg?:?string,image_path?:?string} $d */
    public function create(array $d): array
    {
        $ko = $d['tags_ko'] ?? [];
        $en = $d['tags_en'] ?? [];
        Database::pdo()->prepare(
            'INSERT INTO assets (id, name, category, tags, tags_ko, tags_en, svg, image_path)
             VALUES (:id, :name, :category, :tags, :tags_ko, :tags_en, :svg, :image_path)'
        )->execute([
            ':id'         => $d['id'],
            ':name'       => $d['name'] ?? null,
            ':category'   => $d['category'],
            ':tags'       => json_encode(self::mergeTags($ko, $en), JSON_UNESCAPED_UNICODE),
            ':tags_ko'    => json_encode(array_values($ko), JSON_UNESCAPED_UNICODE),
            ':tags_en'    => json_encode(array_values($en), JSON_UNESCAPED_UNICODE),
            ':svg'        => $d['svg'] ?? null,
            ':image_path' => $d['image_path'] ?? null,
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

        Database::pdo()->prepare(
            'UPDATE assets SET name = :name, category = :category, tags = :tags, tags_ko = :tags_ko, tags_en = :tags_en, image_path = :image_path WHERE id = :id'
        )->execute([
            ':id'         => $id,
            ':name'       => $name,
            ':category'   => $category,
            ':tags'       => json_encode(self::mergeTags($ko, $en), JSON_UNESCAPED_UNICODE),
            ':tags_ko'    => json_encode(array_values($ko), JSON_UNESCAPED_UNICODE),
            ':tags_en'    => json_encode(array_values($en), JSON_UNESCAPED_UNICODE),
            ':image_path' => $image_path,
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
        $row['tags']    = json_decode((string) ($row['tags'] ?? '[]'), true) ?: [];
        $row['tags_ko'] = json_decode((string) ($row['tags_ko'] ?? '[]'), true) ?: [];
        $row['tags_en'] = json_decode((string) ($row['tags_en'] ?? '[]'), true) ?: [];
        // 구 자산(분리 태그 없음)은 통합 tags 를 국문 칸 기본값으로
        if (!$row['tags_ko'] && !$row['tags_en'] && $row['tags']) {
            $row['tags_ko'] = $row['tags'];
        }
        $base = rtrim((string) Config::get('public_base_url', 'https://hom2box.com/powerPlus'), '/');
        $row['image_url'] = !empty($row['image_path'])
            ? $base . '/' . ltrim((string) $row['image_path'], '/')
            : null;
        return $row;
    }
}
