<?php
declare(strict_types=1);

require_once __DIR__ . '/Database.php';

/** 콘텐츠 요청 조회/CRUD. */
final class RequestService
{
    public function create(?string $email, string $type, string $title, string $description, string $link): array
    {
        $pdo = Database::pdo();
        $pdo->prepare(
            'INSERT INTO content_requests (email, type, title, description, link, status, created_at)
             VALUES (:e, :ty, :t, :d, :l, :s, NOW())'
        )->execute([
            ':e' => $email, ':ty' => $type, ':t' => $title,
            ':d' => $description, ':l' => $link, ':s' => 'new',
        ]);
        return $this->find((int) $pdo->lastInsertId()) ?? [];
    }

    /** 관리자: 전체 요청 목록(최신순). */
    public function listAll(): array
    {
        $stmt = Database::pdo()->query(
            'SELECT id, email, type, title, description, link, status, created_at FROM content_requests ORDER BY id DESC'
        );
        return array_map([$this, 'hydrate'], $stmt->fetchAll());
    }

    public function setStatus(int $id, string $status): bool
    {
        $stmt = Database::pdo()->prepare('UPDATE content_requests SET status = :s WHERE id = :id');
        $stmt->execute([':s' => $status, ':id' => $id]);
        return $stmt->rowCount() >= 0;
    }

    public function delete(int $id): bool
    {
        $stmt = Database::pdo()->prepare('DELETE FROM content_requests WHERE id = :id');
        $stmt->execute([':id' => $id]);
        return $stmt->rowCount() > 0;
    }

    /** 처리 대기(new) 요청 수 — 관리자 대시보드 KPI용. */
    public function pendingCount(): int
    {
        return (int) Database::pdo()->query("SELECT COUNT(*) FROM content_requests WHERE status = 'new'")->fetchColumn();
    }

    private function find(int $id): ?array
    {
        $stmt = Database::pdo()->prepare(
            'SELECT id, email, type, title, description, link, status, created_at FROM content_requests WHERE id = :id'
        );
        $stmt->execute([':id' => $id]);
        $row = $stmt->fetch();
        return $row ? $this->hydrate($row) : null;
    }

    private function hydrate(array $row): array
    {
        $row['id'] = (int) $row['id'];
        return $row;
    }
}
