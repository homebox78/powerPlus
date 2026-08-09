<?php
declare(strict_types=1);

require_once __DIR__ . '/AuthService.php';

/** 인증 HTTP 엔드포인트 (이메일 OTP). */
final class AuthController
{
    private AuthService $service;

    public function __construct()
    {
        $this->service = new AuthService();
    }

    /** POST /api/auth/request  body: { email } */
    public function request(array $body): void
    {
        $r = $this->service->requestCode((string) ($body['email'] ?? ''));
        if (!$r['ok']) {
            $this->json(['error' => $r['error'] ?? '요청에 실패했습니다.', 'code' => 400], 400);
            return;
        }
        $out = ['ok' => true, 'message' => '인증코드를 이메일로 보냈습니다.'];
        if (isset($r['dev_code'])) {
            $out['dev_code'] = $r['dev_code']; // auth_debug 일 때만
        }
        $this->json($out);
    }

    /** POST /api/auth/verify  body: { email, code } */
    public function verify(array $body): void
    {
        $r = $this->service->verifyCode(
            (string) ($body['email'] ?? ''),
            (string) ($body['code'] ?? '')
        );
        if (!$r['ok']) {
            $this->json(['error' => $r['error'] ?? '인증에 실패했습니다.', 'code' => 401], 401);
            return;
        }
        $this->json([
            'ok'         => true,
            'token'      => $r['token'],
            'email'      => $r['email'],
            'expires_at' => $r['expires_at'],
        ]);
    }

    /** POST /api/auth/logout  (Authorization: Bearer) */
    public function logout(?string $token): void
    {
        if ($token !== null) {
            $this->service->logout($token);
        }
        $this->json(['ok' => true]);
    }

    private function json(mixed $payload, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    }
}
