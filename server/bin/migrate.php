<?php
declare(strict_types=1);
// DB 마이그레이션 — 멱등(여러 번 실행해도 안전).
// 실행: CLI `php bin/migrate.php` 또는 웹루트 임시 사본 + ?key=(config의 import_key) — 웹 실행은 키 필수.
$srcDir = is_dir(__DIR__ . '/src') ? __DIR__ . '/src' : __DIR__ . '/../src'; // 웹루트 사본/원위치 모두 지원
require_once $srcDir . '/Config.php';
require_once $srcDir . '/Database.php';
if (PHP_SAPI !== 'cli') {
    $IMPORT_KEY = (string) Config::get('import_key', '');
    if ($IMPORT_KEY === '' || !hash_equals($IMPORT_KEY, (string) ($_GET['key'] ?? ''))) { http_response_code(404); exit; }
    header('Content-Type: text/plain; charset=utf-8');
}

$pdo = Database::pdo();

// 카테고리 테이블
$pdo->exec("CREATE TABLE IF NOT EXISTS categories (
  `key` VARCHAR(32) NOT NULL PRIMARY KEY,
  label VARCHAR(64) NOT NULL,
  sort_order INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");
$pdo->exec("INSERT IGNORE INTO categories (`key`,label,sort_order) VALUES
  ('icon','아이콘',1),('photo','사진',2),('illust','일러스트',3),('diagram','다이어그램',4),('ppt','장표',5),('logo','로고',6)");

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

// 일별 방문 기록 — 인증 시 사용자×날짜 1행(UNIQUE)으로 누적 → 일/월/년 방문자수 통계
$pdo->exec("CREATE TABLE IF NOT EXISTS visits (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NULL,
  day DATE NOT NULL,
  visited_at DATETIME NOT NULL,
  UNIQUE KEY uniq_day_email (day, email),
  INDEX idx_day (day)
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

// 장표(ppt) 세분화: 유형(패키지/단일) + 페이지 종류(표지/목차/간지/콘텐츠/인사말/qa/기타)
foreach (['slide_kind' => 'VARCHAR(16)', 'slide_page' => 'VARCHAR(32)'] as $col => $type) {
    $has = (int) $pdo->query(
        "SELECT COUNT(*) FROM information_schema.COLUMNS
         WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='assets' AND COLUMN_NAME='$col'"
    )->fetchColumn();
    if ($has === 0) {
        $pdo->exec("ALTER TABLE assets ADD COLUMN $col $type NULL AFTER slide_path");
    }
}

// 등록 시각 — '최신순'을 카테고리 무관 실제 등록순으로 정렬하기 위함(없으면 id로 폴백)
$hasCreated = (int) $pdo->query(
    "SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='assets' AND COLUMN_NAME='created_at'"
)->fetchColumn();
if ($hasCreated === 0) {
    $pdo->exec("ALTER TABLE assets ADD COLUMN created_at DATETIME NULL");
    $pdo->exec("ALTER TABLE assets ADD INDEX idx_created (created_at)");
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

// 검색 로그 — 검색 품질(무결과율)·수요 파악용. 무결과 검색어가 자산 확충/임베딩 도입의 근거 데이터.
$pdo->exec("CREATE TABLE IF NOT EXISTS search_logs (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NULL,
  query VARCHAR(255) NOT NULL,
  category VARCHAR(32) NULL,
  results INT NOT NULL DEFAULT 0,
  searched_at DATETIME NOT NULL,
  INDEX idx_time (searched_at),
  INDEX idx_query (query(64)),
  INDEX idx_zero (results, searched_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");

// user_favorites.asset_id 인덱스 — fav_count 서브쿼리·순위 JOIN이 PK(email 선두)로는 풀스캔이라 필수
$hasFavIdx = (int) $pdo->query(
    "SELECT COUNT(*) FROM information_schema.STATISTICS
     WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='user_favorites' AND INDEX_NAME='idx_asset'"
)->fetchColumn();
if ($hasFavIdx === 0) {
    $pdo->exec("ALTER TABLE user_favorites ADD INDEX idx_asset (asset_id)");
}

// usage_log.email 인덱스 — PrefsService::recent()가 WHERE email = :e 로 조회하는데
// 기존 인덱스는 idx_asset/idx_used 뿐이라 풀스캔. 로그는 계속 쌓이므로 시간이 갈수록 느려진다.
$hasUsageEmailIdx = (int) $pdo->query(
    "SELECT COUNT(*) FROM information_schema.STATISTICS
     WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='usage_log' AND INDEX_NAME='idx_email'"
)->fetchColumn();
if ($hasUsageEmailIdx === 0) {
    // (email, asset_id, used_at) 복합 = 이 쿼리의 커버링 인덱스(조회·그룹·정렬 컬럼 전부 포함)
    $pdo->exec("ALTER TABLE usage_log ADD INDEX idx_email (email, asset_id, used_at)");
}

echo "migrate OK\n";
echo "categories:\n";
foreach ($pdo->query("SELECT `key`,label,sort_order FROM categories ORDER BY sort_order") as $r) {
    echo "  {$r['key']} / {$r['label']} / {$r['sort_order']}\n";
}
