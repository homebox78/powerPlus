<?php
declare(strict_types=1);

require_once __DIR__ . '/Database.php';

/** 사용자별 즐겨찾기 / 최근 사용. 최근은 usage_log 에서 파생(별도 저장 없음). */
final class PrefsService
{
    /** @return string[] 즐겨찾기 자산 ID (최근 추가순) */
    public function favorites(string $email): array
    {
        $stmt = Database::pdo()->prepare(
            'SELECT asset_id FROM user_favorites WHERE email = :e ORDER BY created_at DESC'
        );
        $stmt->execute([':e' => $email]);
        return array_map('strval', $stmt->fetchAll(PDO::FETCH_COLUMN));
    }

    public function addFavorite(string $email, string $assetId): void
    {
        Database::pdo()->prepare(
            'INSERT IGNORE INTO user_favorites (email, asset_id, created_at) VALUES (:e, :a, NOW())'
        )->execute([':e' => $email, ':a' => $assetId]);
    }

    public function removeFavorite(string $email, string $assetId): void
    {
        Database::pdo()->prepare(
            'DELETE FROM user_favorites WHERE email = :e AND asset_id = :a'
        )->execute([':e' => $email, ':a' => $assetId]);
    }

    /** @return string[] 최근 사용(삽입) 자산 ID, 최신순 중복제거. usage_log 파생. */
    public function recent(string $email, int $limit = 20): array
    {
        $limit = max(1, min(100, $limit)); // 정수 캐스팅 후 인라인 — 안전
        $stmt = Database::pdo()->prepare(
            "SELECT asset_id FROM usage_log WHERE email = :e
             GROUP BY asset_id ORDER BY MAX(used_at) DESC LIMIT $limit"
        );
        $stmt->execute([':e' => $email]);
        return array_map('strval', $stmt->fetchAll(PDO::FETCH_COLUMN));
    }
}
