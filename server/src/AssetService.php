<?php
declare(strict_types=1);

require_once __DIR__ . '/Database.php';

/** 자산 조회/검색 로직. SQL은 모두 prepared statement. */
final class AssetService
{
    /**
     * 카테고리 + 검색어 필터 + 페이지네이션.
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
            // 이름 또는 태그(JSON 텍스트) 부분일치
            $where[] = '(name LIKE :q OR tags LIKE :q)';
            $params[':q'] = '%' . $q . '%';
        }
        $whereSql = $where ? ('WHERE ' . implode(' AND ', $where)) : '';

        $countStmt = $pdo->prepare("SELECT COUNT(*) FROM assets $whereSql");
        $countStmt->execute($params);
        $total = (int) $countStmt->fetchColumn();

        $offset = ($page - 1) * $limit;
        $stmt = $pdo->prepare(
            "SELECT id, name, category, tags, svg FROM assets $whereSql ORDER BY id LIMIT :limit OFFSET :offset"
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
        $stmt = Database::pdo()->prepare(
            'SELECT id, name, category, tags, svg FROM assets WHERE id = :id'
        );
        $stmt->execute([':id' => $id]);
        $row = $stmt->fetch();
        return $row ? $this->hydrate($row) : null;
    }

    /** tags(JSON 문자열) → 배열로 변환 */
    private function hydrate(array $row): array
    {
        $row['tags'] = json_decode((string) ($row['tags'] ?? '[]'), true) ?: [];
        return $row;
    }
}
