-- powerPlus 인증(이메일 OTP) 테이블
-- 적용: phpMyAdmin에서 powerplus DB 선택 후 이 파일 실행
--   또는 mysql -u root -p powerplus < sql/auth.sql

-- 발급된 1회용 인증코드 (해시로 저장, 만료/시도횟수 관리)
CREATE TABLE IF NOT EXISTS auth_codes (
  id         BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email      VARCHAR(255) NOT NULL,
  code_hash  CHAR(64)     NOT NULL,           -- sha256(6자리 코드)
  expires_at DATETIME     NOT NULL,
  attempts   INT          NOT NULL DEFAULT 0, -- 틀린 입력 횟수
  created_at DATETIME     NOT NULL,
  INDEX idx_email (email),
  INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 로그인 세션 토큰 (해시로 저장)
CREATE TABLE IF NOT EXISTS sessions (
  token_hash   CHAR(64)     NOT NULL PRIMARY KEY, -- sha256(토큰)
  email        VARCHAR(255) NOT NULL,
  expires_at   DATETIME     NOT NULL,
  created_at   DATETIME     NOT NULL,
  last_used_at DATETIME     NULL,
  INDEX idx_email (email),
  INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
