<?php
declare(strict_types=1);
// DB 마이그레이션 — 서버에서 `php bin/migrate.php` 로 실행. 멱등(여러 번 실행해도 안전).
require_once __DIR__ . '/../src/Database.php';

$pdo = Database::pdo();

// 카테고리 테이블
$pdo->exec("CREATE TABLE IF NOT EXISTS categories (
  `key` VARCHAR(32) NOT NULL PRIMARY KEY,
  label VARCHAR(64) NOT NULL,
  sort_order INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");
$pdo->exec("INSERT IGNORE INTO categories (`key`,label,sort_order) VALUES
  ('icon','아이콘',1),('photo','사진',2),('illust','일러스트',3),('diagram','다이어그램',4),('ppt','장표',5)");

// 썸네일 경로 컬럼 (목록 표시용 축소 이미지 — 삽입은 원본 image_path 사용)
$hasThumb = (int) $pdo->query(
    "SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='assets' AND COLUMN_NAME='thumb_path'"
)->fetchColumn();
if ($hasThumb === 0) {
    $pdo->exec("ALTER TABLE assets ADD COLUMN thumb_path VARCHAR(255) NULL AFTER image_path");
}

// 장표(ppt) 자산용 슬라이드 파일 경로 컬럼
$hasSlide = (int) $pdo->query(
    "SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='assets' AND COLUMN_NAME='slide_path'"
)->fetchColumn();
if ($hasSlide === 0) {
    $pdo->exec("ALTER TABLE assets ADD COLUMN slide_path VARCHAR(255) NULL AFTER image_path");
}

// 사용 통계 로그 테이블 (Phase: 통계)
$pdo->exec("CREATE TABLE IF NOT EXISTS usage_log (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  asset_id VARCHAR(64) NOT NULL,
  email VARCHAR(255) NULL,
  used_at DATETIME NOT NULL,
  INDEX idx_asset (asset_id),
  INDEX idx_used (used_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");

// assets 테이블: 업로드 이미지 경로 컬럼 추가 + svg/name 을 선택값(NULL 허용)으로
$hasCol = (int) $pdo->query(
    "SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='assets' AND COLUMN_NAME='image_path'"
)->fetchColumn();
if ($hasCol === 0) {
    $pdo->exec("ALTER TABLE assets ADD COLUMN image_path VARCHAR(255) NULL AFTER svg");
}
$pdo->exec("ALTER TABLE assets MODIFY svg MEDIUMTEXT NULL");
$pdo->exec("ALTER TABLE assets MODIFY name VARCHAR(255) NULL");

// 사용자별 즐겨찾기 (이메일 + 자산). 최근은 usage_log 재활용하므로 별도 테이블 불필요.
$pdo->exec("CREATE TABLE IF NOT EXISTS user_favorites (
  email VARCHAR(255) NOT NULL,
  asset_id VARCHAR(64) NOT NULL,
  created_at DATETIME NOT NULL,
  PRIMARY KEY (email, asset_id),
  INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");

// 국문/영문 분리 태그 컬럼
foreach (['tags_ko', 'tags_en'] as $c) {
    $has = (int) $pdo->query(
        "SELECT COUNT(*) FROM information_schema.COLUMNS
         WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='assets' AND COLUMN_NAME='$c'"
    )->fetchColumn();
    if ($has === 0) {
        $pdo->exec("ALTER TABLE assets ADD COLUMN $c JSON NULL AFTER tags");
    }
}

// 공지(알람) 테이블 — 관리자가 등록, 사용자 애드인 우측상단 알람에 표시
$pdo->exec("CREATE TABLE IF NOT EXISTS announcements (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  body TEXT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NULL,
  INDEX idx_active (is_active, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");

// 콘텐츠 요청 테이블 — 사용자가 필요한 자료를 요청, 관리자가 검토
$pdo->exec("CREATE TABLE IF NOT EXISTS content_requests (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NULL,
  type VARCHAR(32) NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT NULL,
  link VARCHAR(500) NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'new',
  created_at DATETIME NOT NULL,
  INDEX idx_status (status, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");

echo "migrate OK\n";
echo "categories:\n";
foreach ($pdo->query("SELECT `key`,label,sort_order FROM categories ORDER BY sort_order") as $r) {
    echo "  {$r['key']} / {$r['label']} / {$r['sort_order']}\n";
}
