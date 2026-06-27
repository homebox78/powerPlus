-- powerPlus 카테고리 테이블 (동적 관리)
-- 적용: phpMyAdmin 또는  php bin/migrate.php

CREATE TABLE IF NOT EXISTS categories (
  `key`      VARCHAR(32) NOT NULL PRIMARY KEY,
  label      VARCHAR(64) NOT NULL,
  sort_order INT         NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 기존 4개 시드 (이미 있으면 무시)
INSERT IGNORE INTO categories (`key`, label, sort_order) VALUES
  ('icon',    '아이콘',     1),
  ('photo',   '사진',       2),
  ('illust',  '일러스트',   3),
  ('diagram', '다이어그램', 4);
