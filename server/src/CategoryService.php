<?php
declare(strict_types=1);

require_once __DIR__ . '/Database.php';

/** 카테고리 조회/관리. SQL 은 prepared statement. (`key` 는 예약어라 백틱) */
final class CategoryService
{
    /** @return array<int,array{key:string,label:string,sort_order:int}> */
    public function all(): array
    {
        $rows = Database::pdo()
            ->query('SELECT `key`, label, sort_order FROM categories ORDER BY sort_order, `key`')
            ->fetchAll();
        return array_map(static fn($r) => [
            'key'        => $r['key'],
            'label'      => $r['label'],
            'sort_order' => (int) $r['sort_order'],
        ], $rows);
    }

    /**
     * 카테고리 목록 + 등록 수(카운트 1회 집계로 붙인다 — 카테고리마다 세면 N+1).
     * @return array<int,array{key:string,label:string,sort_order:int,count:int}>
     */
    public function allWithCounts(): array
    {
        $counts = [];
        foreach (Database::pdo()->query('SELECT category, COUNT(*) n FROM assets GROUP BY category')->fetchAll() as $r) {
            $counts[(string) $r['category']] = (int) $r['n'];
        }
        return array_map(static fn($c) => $c + ['count' => $counts[$c['key']] ?? 0], $this->all());
    }

    public function exists(string $key): bool
    {
        $stmt = Database::pdo()->prepare('SELECT 1 FROM categories WHERE `key` = :k');
        $stmt->execute([':k' => $key]);
        return (bool) $stmt->fetchColumn();
    }

    /** 해당 카테고리를 쓰는 자산 수 */
    public function assetCount(string $key): int
    {
        $stmt = Database::pdo()->prepare('SELECT COUNT(*) FROM assets WHERE category = :k');
        $stmt->execute([':k' => $key]);
        return (int) $stmt->fetchColumn();
    }

    public function create(string $key, string $label, int $sort): void
    {
        Database::pdo()
            ->prepare('INSERT INTO categories (`key`, label, sort_order) VALUES (:k, :l, :s)')
            ->execute([':k' => $key, ':l' => $label, ':s' => $sort]);
    }

    public function update(string $key, string $label, int $sort): void
    {
        Database::pdo()
            ->prepare('UPDATE categories SET label = :l, sort_order = :s WHERE `key` = :k')
            ->execute([':k' => $key, ':l' => $label, ':s' => $sort]);
    }

    public function delete(string $key): void
    {
        Database::pdo()->prepare('DELETE FROM categories WHERE `key` = :k')->execute([':k' => $key]);
    }
}
