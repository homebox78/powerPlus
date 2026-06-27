-- powerPlus 자산 테이블
-- 적용: mysql -u root -p powerplus < sql/schema.sql

CREATE DATABASE IF NOT EXISTS powerplus
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE powerplus;

CREATE TABLE IF NOT EXISTS assets (
  id        VARCHAR(64)  NOT NULL PRIMARY KEY,
  name      VARCHAR(255) NOT NULL,
  category  VARCHAR(32)  NOT NULL,
  tags      JSON         NOT NULL,
  svg       MEDIUMTEXT   NOT NULL,
  INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
