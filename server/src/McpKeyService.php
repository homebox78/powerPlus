<?php
declare(strict_types=1);

require_once __DIR__ . '/Database.php';

/**
 * MCP 접속 키 — 외부 솔루션·AI 클라이언트(Claude·Cursor 등)가 /mcp 에 붙을 때 쓰는 키.
 *
 * - 원문은 발급 순간 한 번만 보여주고 DB 에는 sha256 해시만 저장한다(유출돼도 재사용 불가).
 * - 관리자가 발급·폐기한다. 폐기는 삭제가 아니라 revoked_at 기록(사용 이력 보존).
 * - 키마다 호출 수·마지막 사용 시각을 남겨 어느 연동이 얼마나 쓰는지 본다.
 */
final class McpKeyService
{
    public const PREFIX = 'pp_mcp_';

    public static function ensureTable(): void
    {
        Database::pdo()->exec("CREATE TABLE IF NOT EXISTS mcp_keys (
          id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          name VARCHAR(100) NOT NULL,
          key_hash CHAR(64) NOT NULL,
          key_hint VARCHAR(24) NOT NULL,
          created_by VARCHAR(255) NULL,
          created_at DATETIME NOT NULL,
          last_used_at DATETIME NULL,
          uses INT NOT NULL DEFAULT 0,
          revoked_at DATETIME NULL,
          UNIQUE KEY uniq_hash (key_hash)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");
    }

    /** @return array<int,array<string,mixed>> */
    public function all(): array
    {
        self::ensureTable();
        $rows = Database::pdo()->query(
            'SELECT id, name, key_hint, created_by, created_at, last_used_at, uses, revoked_at
               FROM mcp_keys ORDER BY revoked_at IS NOT NULL, id DESC'
        )->fetchAll();
        foreach ($rows as &$r) { $r['id'] = (int) $r['id']; $r['uses'] = (int) $r['uses']; }
        return $rows;
    }

    /** 새 키 발급 — 반환값의 key(원문)는 이 응답에서만 볼 수 있다. */
    public function create(string $name, ?string $by): array
    {
        self::ensureTable();
        $key  = self::PREFIX . bin2hex(random_bytes(20));
        $hint = substr($key, 0, 11) . '…' . substr($key, -4);
        Database::pdo()->prepare(
            'INSERT INTO mcp_keys (name, key_hash, key_hint, created_by, created_at)
             VALUES (:n, :h, :t, :b, NOW())'
        )->execute([':n' => $name, ':h' => hash('sha256', $key), ':t' => $hint, ':b' => $by]);
        return ['id' => (int) Database::pdo()->lastInsertId(), 'name' => $name, 'key' => $key, 'key_hint' => $hint];
    }

    public function revoke(int $id): bool
    {
        self::ensureTable();
        $st = Database::pdo()->prepare('UPDATE mcp_keys SET revoked_at = NOW() WHERE id = :id AND revoked_at IS NULL');
        $st->execute([':id' => $id]);
        return $st->rowCount() > 0;
    }

    /** 유효한 키면 키 정보(id·name), 아니면 null. 호출 수·마지막 사용 시각을 함께 갱신한다. */
    public function verify(string $key): ?array
    {
        if (!str_starts_with($key, self::PREFIX)) return null;
        self::ensureTable();
        $st = Database::pdo()->prepare(
            'SELECT id, name FROM mcp_keys WHERE key_hash = :h AND revoked_at IS NULL'
        );
        $st->execute([':h' => hash('sha256', $key)]);
        $row = $st->fetch();
        if (!$row) return null;
        try {
            Database::pdo()->prepare('UPDATE mcp_keys SET uses = uses + 1, last_used_at = NOW() WHERE id = :id')
                ->execute([':id' => $row['id']]);
        } catch (Throwable $e) { /* 사용량 기록 실패가 호출을 막지 않게 */ }
        return ['id' => (int) $row['id'], 'name' => (string) $row['name']];
    }
}
