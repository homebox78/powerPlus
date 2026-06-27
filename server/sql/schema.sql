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

-- 인증(이메일 OTP) 테이블 — 발급 코드 / 로그인 세션
CREATE TABLE IF NOT EXISTS auth_codes (
  id         BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email      VARCHAR(255) NOT NULL,
  code_hash  CHAR(64)     NOT NULL,
  expires_at DATETIME     NOT NULL,
  attempts   INT          NOT NULL DEFAULT 0,
  created_at DATETIME     NOT NULL,
  INDEX idx_email (email),
  INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sessions (
  token_hash   CHAR(64)     NOT NULL PRIMARY KEY,
  email        VARCHAR(255) NOT NULL,
  expires_at   DATETIME     NOT NULL,
  created_at   DATETIME     NOT NULL,
  last_used_at DATETIME     NULL,
  INDEX idx_email (email),
  INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
