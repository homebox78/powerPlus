<?php
declare(strict_types=1);

require_once __DIR__ . '/Database.php';
require_once __DIR__ . '/Config.php';
require_once __DIR__ . '/Mailer.php';

/**
 * 이메일 OTP 인증. 코드/토큰은 모두 sha256 해시로 저장하고
 * SQL 은 prepared statement, 시간 계산은 MySQL NOW() 기준으로 통일한다.
 */
final class AuthService
{
    /**
     * 인증코드 요청: 이메일 형식/도메인 검증 → 코드 생성·저장·메일 발송.
     * @return array{ok:bool, error?:string, dev_code?:string}
     */
    public function requestCode(string $email): array
    {
        $email = strtolower(trim($email));
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            return ['ok' => false, 'error' => '올바른 이메일 형식이 아닙니다.'];
        }
        $domain = strtolower((string) Config::get('allowed_domain', ''));
        if ($domain !== '' && !str_ends_with($email, '@' . $domain)) {
            return ['ok' => false, 'error' => '@' . $domain . ' 이메일만 사용할 수 있습니다.'];
        }

        $pdo = Database::pdo();

        // 속도 제한: 최근 60초 내 발송 이력이 있으면 거부
        $recent = $pdo->prepare(
            'SELECT COUNT(*) FROM auth_codes WHERE email = :e AND created_at > (NOW() - INTERVAL 60 SECOND)'
        );
        $recent->execute([':e' => $email]);
        if ((int) $recent->fetchColumn() > 0) {
            return ['ok' => false, 'error' => '잠시 후 다시 시도해 주세요. (1분에 한 번)'];
        }

        $code   = str_pad((string) random_int(0, 999999), 6, '0', STR_PAD_LEFT);
        $ttlMin = max(1, (int) Config::get('code_ttl_min', 10)); // 정수 캐스팅 → INTERVAL 인라인 안전

        // 이전 미사용 코드 정리 후 새 코드 저장
        $pdo->prepare('DELETE FROM auth_codes WHERE email = :e')->execute([':e' => $email]);
        $pdo->prepare(
            "INSERT INTO auth_codes (email, code_hash, expires_at, attempts, created_at)
             VALUES (:e, :h, DATE_ADD(NOW(), INTERVAL $ttlMin MINUTE), 0, NOW())"
        )->execute([':e' => $email, ':h' => hash('sha256', $code)]);

        $subject = 'powerPlus 인증코드: ' . $code;
        $body = "powerPlus 로그인 인증코드입니다.\n\n"
              . "인증코드: {$code}\n\n"
              . "이 코드는 {$ttlMin}분간 유효합니다.\n"
              . "본인이 요청하지 않았다면 이 메일을 무시하세요.";

        // 개발 모드: 메일이 안 가도 코드 확인 가능하도록 로그 + 응답에 포함
        if (Config::bool('auth_debug')) {
            @file_put_contents(
                __DIR__ . '/../logs/auth-codes.log',
                date('c') . " {$email} {$code}\n",
                FILE_APPEND
            );
            return ['ok' => true, 'dev_code' => $code];
        }

        if (!Mailer::send($email, $subject, $body)) {
            return ['ok' => false, 'error' => '메일 발송에 실패했습니다. 관리자에게 문의하세요.'];
        }
        return ['ok' => true];
    }

    /**
     * 인증코드 검증 → 성공 시 세션 토큰 발급.
     * @return array{ok:bool, error?:string, token?:string, email?:string, expires_at?:string}
     */
    public function verifyCode(string $email, string $code): array
    {
        $email = strtolower(trim($email));
        $code  = trim($code);
        $pdo   = Database::pdo();

        $stmt = $pdo->prepare(
            'SELECT id, code_hash, attempts FROM auth_codes
             WHERE email = :e AND expires_at > NOW()
             ORDER BY id DESC LIMIT 1'
        );
        $stmt->execute([':e' => $email]);
        $row = $stmt->fetch();

        if (!$row) {
            return ['ok' => false, 'error' => '인증코드가 만료되었거나 없습니다. 다시 요청해 주세요.'];
        }
        if ((int) $row['attempts'] >= 5) {
            $pdo->prepare('DELETE FROM auth_codes WHERE email = :e')->execute([':e' => $email]);
            return ['ok' => false, 'error' => '시도 횟수를 초과했습니다. 코드를 다시 요청해 주세요.'];
        }
        if (!hash_equals((string) $row['code_hash'], hash('sha256', $code))) {
            $pdo->prepare('UPDATE auth_codes SET attempts = attempts + 1 WHERE id = :id')
                ->execute([':id' => $row['id']]);
            return ['ok' => false, 'error' => '인증코드가 일치하지 않습니다.'];
        }

        // 성공 — 코드 폐기, 세션 토큰 발급
        $pdo->prepare('DELETE FROM auth_codes WHERE email = :e')->execute([':e' => $email]);

        $token   = bin2hex(random_bytes(32));
        $hash    = hash('sha256', $token);
        $ttlDays = max(1, (int) Config::get('session_ttl_days', 30));

        $pdo->prepare(
            "INSERT INTO sessions (token_hash, email, expires_at, created_at)
             VALUES (:h, :e, DATE_ADD(NOW(), INTERVAL $ttlDays DAY), NOW())"
        )->execute([':h' => $hash, ':e' => $email]);

        $exp = $pdo->prepare('SELECT expires_at FROM sessions WHERE token_hash = :h');
        $exp->execute([':h' => $hash]);

        return [
            'ok'         => true,
            'token'      => $token,
            'email'      => $email,
            'expires_at' => (string) $exp->fetchColumn(),
        ];
    }

    /** 토큰 검증 → 이메일 반환. 유효하지 않으면 null. */
    public function validateToken(string $token): ?string
    {
        $token = trim($token);
        if ($token === '') {
            return null;
        }
        $hash = hash('sha256', $token);
        $pdo  = Database::pdo();

        $stmt = $pdo->prepare(
            'SELECT email FROM sessions WHERE token_hash = :h AND expires_at > NOW() LIMIT 1'
        );
        $stmt->execute([':h' => $hash]);
        $email = $stmt->fetchColumn();
        if ($email === false) {
            return null;
        }
        $pdo->prepare('UPDATE sessions SET last_used_at = NOW() WHERE token_hash = :h')
            ->execute([':h' => $hash]);
        return (string) $email;
    }

    public function logout(string $token): void
    {
        $token = trim($token);
        if ($token === '') {
            return;
        }
        Database::pdo()->prepare('DELETE FROM sessions WHERE token_hash = :h')
            ->execute([':h' => hash('sha256', $token)]);
    }
}
