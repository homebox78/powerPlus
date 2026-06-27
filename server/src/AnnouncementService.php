<?php
declare(strict_types=1);

require_once __DIR__ . '/Database.php';

/** 공지(알람) 조회/CRUD. 모두 prepared statement. */
final class AnnouncementService
{
    /** 활성 공지(사용자용) — 최신순. */
    public function listActive(): array
    {
        $stmt = Database::pdo()->query(
            'SELECT id, title, body, created_at FROM announcements WHERE is_active = 1 ORDER BY id DESC'
        );
        return array_map([$this, 'hydrate'], $stmt->fetchAll());
    }

    /** 전체 공지(관리자용) — 최신순. */
    public function listAll(): array
    {
        $stmt = Database::pdo()->query(
            'SELECT id, title, body, is_active, created_at, updated_at FROM announcements ORDER BY id DESC'
        );
        return array_map([$this, 'hydrate'], $stmt->fetchAll());
    }

    public function create(string $title, string $body, bool $active): array
    {
        $pdo = Database::pdo();
        $pdo->prepare(
            'INSERT INTO announcements (title, body, is_active, created_at) VALUES (:t, :b, :a, NOW())'
        )->execute([':t' => $title, ':b' => $body, ':a' => $active ? 1 : 0]);
        return $this->find((int) $pdo->lastInsertId()) ?? [];
    }

    public function update(int $id, string $title, string $body, bool $active): bool
    {
        $stmt = Database::pdo()->prepare(
            'UPDATE announcements SET title = :t, body = :b, is_active = :a, updated_at = NOW() WHERE id = :id'
        );
        $stmt->execute([':t' => $title, ':b' => $body, ':a' => $active ? 1 : 0, ':id' => $id]);
        return $stmt->rowCount() >= 0;
    }

    public function delete(int $id): bool
    {
        $stmt = Database::pdo()->prepare('DELETE FROM announcements WHERE id = :id');
        $stmt->execute([':id' => $id]);
        return $stmt->rowCount() > 0;
    }

    private function find(int $id): ?array
    {
        $stmt = Database::pdo()->prepare(
            'SELECT id, title, body, is_active, created_at, updated_at FROM announcements WHERE id = :id'
        );
        $stmt->execute([':id' => $id]);
        $row = $stmt->fetch();
        return $row ? $this->hydrate($row) : null;
    }

    private function hydrate(array $row): array
    {
        $row['id'] = (int) $row['id'];
        if (array_key_exists('is_active', $row)) {
            $row['is_active'] = (int) $row['is_active'];
        }
        return $row;
    }
}
