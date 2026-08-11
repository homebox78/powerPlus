<?php
/**
 * powerPlus 서버 설정 템플릿.
 *
 * 이 파일을 같은 폴더에 config.php 로 복사한 뒤 실제 값을 채운다.
 *   cp config/config.example.php config/config.php
 *
 * ⚠️ config.php 는 git 제외(.gitignore). 실제 비밀번호·키를 이 예제 파일에 적지 말 것
 *    (repo 가 공개라 그대로 노출된다). 여기엔 항상 플레이스홀더만 둔다.
 * 💡 같은 이름의 환경변수(대문자)가 있으면 그쪽이 우선한다. 예: ALLOWED_DOMAIN, IMPORT_KEY
 */
return [
    // ── DB (PDO/MySQL) ────────────────────────────────────────────────
    'host' => 'localhost',
    'port' => 3306,
    'db'   => 'powerplus',
    'user' => 'DB_사용자명',
    'pass' => 'DB_비밀번호',

    // ── 로그인 정책 (이메일 OTP) ───────────────────────────────────────
    // 기본: 회사 도메인만 허용. 빈 문자열이면 도메인 제한 없음.
    'allowed_domain'  => 'example.com',
    // 도메인을 더 허용하려면 배열로(협력사·계열사 등). allowed_domain 과 합쳐진다.
    'allowed_domains' => [],
    // 도메인과 무관하게 상시 허용할 개별 이메일.
    'allowed_emails'  => [],

    // 한시 개방(해커톤 심사 등) — 이 날짜(YYYY-MM-DD)까지 도메인 제한을 완화한다.
    //  · open_emails 가 비어 있으면 기간 내 모든 이메일 허용
    //  · open_emails 에 값이 있으면 그 이메일만 추가 허용
    //  · 날짜가 지나면 자동으로 원래 정책으로 복귀(설정을 지우지 않아도 안전)
    'open_until'  => '',   // 예: '2026-09-30'
    'open_emails' => [],   // 예: ['judge1@company.com']

    'code_ttl_min'     => 10,   // 인증코드 유효 시간(분)
    'session_ttl_days' => 30,   // 로그인 세션 유지(일)
    'auth_debug'       => false, // true 면 인증코드를 응답·로그에 노출 — 운영에선 반드시 false

    // 관리자 대시보드 접근 이메일. 환경변수로 줄 때는 콤마 구분 문자열도 가능.
    'admin_emails' => ['admin@example.com'],

    // ── 메일 발송 (SMTP, PHPMailer) ───────────────────────────────────
    'smtp_host'   => 'smtp.gmail.com',
    'smtp_port'   => 587,
    'smtp_user'   => 'SMTP_계정',
    'smtp_pass'   => 'SMTP_앱비밀번호',
    'smtp_secure' => 'tls',
    'mail_from'      => 'no-reply@example.com',
    'mail_from_name' => 'powerPlus',

    // ── 기타 ──────────────────────────────────────────────────────────
    // 서비스 공개 주소(메일 링크 등에 사용).
    'public_base_url' => 'https://example.com/powerPlus',
    // bin/ 유지보수 스크립트(migrate·import·enrich) 실행 키. 비우면 항상 404 로 막힌다.
    'import_key' => '', // 예: bin2hex(random_bytes(24)) 로 생성한 긴 랜덤 문자열
];
