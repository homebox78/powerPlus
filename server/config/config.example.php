<?php
// 이 파일을 config.php 로 "복사"한 뒤 실제 값으로 채우세요. (config.php 는 git 제외)
// 환경변수(DB_HOST, ALLOWED_DOMAIN 등)가 있으면 그쪽이 우선합니다.
return [
    // ── 데이터베이스 ──
    'host' => '127.0.0.1',
    'port' => 3306,
    'db'   => 'powerplus',
    'user' => 'root',
    'pass' => '',

    // ── 인증 (이메일 OTP) ──
    // 이 도메인 이메일만 로그인 허용. 빈 문자열이면 도메인 제한 없음.
    'allowed_domain'   => 'solideos.com',
    'code_ttl_min'     => 10,   // 인증코드 유효시간(분)
    'session_ttl_days' => 30,   // 로그인 유지(일)

    // ── 메일 발송 ──
    'mail_from'      => 'noreply@hom2box.com',
    'mail_from_name' => 'powerPlus',

    // SMTP: smtp_host 가 비어있으면 PHP mail() 사용, 값이 있으면 SMTP(PHPMailer) 사용.
    // 공유호스팅은 mail() 이 막힌 경우가 많으니 호스팅 메일계정 SMTP 정보를 채우세요.
    'smtp_host'   => '',          // 예: mail.hom2box.com
    'smtp_port'   => 587,         // 587(STARTTLS) 또는 465(SSL)
    'smtp_user'   => '',          // 메일 계정 (예: noreply@hom2box.com)
    'smtp_pass'   => '',          // 메일 계정 비밀번호
    'smtp_secure' => 'tls',       // 'tls'(587) 또는 'ssl'(465)

    // 개발용: mail()/SMTP 없이 인증코드를 응답/로그로 확인.
    // !!! 운영 서버에서는 반드시 false !!!
    'auth_debug'     => false,
];
