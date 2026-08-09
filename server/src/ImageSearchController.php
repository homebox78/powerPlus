<?php
declare(strict_types=1);

/**
 * 무료 이미지 검색(Openverse) — 작업창 안 이미지 검색 + 삽입용.
 *  - search(): Openverse API 프록시(JSON). 로그인 사용자 전용.
 *  - proxy() : 외부 이미지 바이트를 동일 출처로 중계(CORS 회피 + 삽입용 base64 변환). 로그인 사용자 전용.
 * Openverse: 키 불필요, 상업적 사용 가능(라이선스 표기 권장).
 */
final class ImageSearchController
{
    /** GET /api/imagesearch?q=&page= */
    public function search(array $query): void
    {
        $q = trim((string) ($query['q'] ?? ''));
        $page = max(1, min(20, (int) ($query['page'] ?? 1)));
        if ($q === '') {
            $this->json(['data' => [], 'total' => 0, 'page' => 1]);
            return;
        }
        $url = 'https://api.openverse.org/v1/images/?' . http_build_query([
            'q'         => $q,
            'page_size' => 20,
            'page'      => $page,
            'mature'    => 'false',
        ]);
        [$body, $code, $ctype] = $this->httpGet($url, 12, ['Accept: application/json', 'User-Agent: powerPlus/1.0']);
        if ($body === null || $code >= 400) {
            $this->json(['error' => '이미지 검색에 실패했습니다.', 'code' => 502], 502);
            return;
        }
        $j = json_decode($body, true);
        $out = [];
        foreach (($j['results'] ?? []) as $r) {
            $full = (string) ($r['url'] ?? '');
            if ($full === '') continue;
            $out[] = [
                'id'      => (string) ($r['id'] ?? ''),
                'title'   => (string) ($r['title'] ?? ''),
                'thumb'   => (string) ($r['thumbnail'] ?? $full),
                'url'     => $full,
                'source'  => (string) ($r['source'] ?? ''),
                'creator' => (string) ($r['creator'] ?? ''),
                'license' => (string) ($r['license'] ?? ''),
                'landing' => (string) ($r['foreign_landing_url'] ?? ''),
            ];
        }
        $this->json(['data' => $out, 'total' => (int) ($j['result_count'] ?? count($out)), 'page' => $page]);
    }

    /** GET /api/imageproxy?url=  — 외부 이미지 바이트 중계(이미지 콘텐츠만). 삽입 시 동일 출처 fetch용. */
    public function proxy(array $query): void
    {
        $u = (string) ($query['url'] ?? '');
        if (!preg_match('#^https://#i', $u)) {
            http_response_code(400);
            echo 'bad url';
            return;
        }
        $host = (string) parse_url($u, PHP_URL_HOST);
        if ($host === '' || $this->isBlockedHost($host)) {
            http_response_code(403);
            echo 'blocked host';
            return;
        }
        [$body, $code, $ctype] = $this->httpGet($u, 15, ['User-Agent: powerPlus/1.0'], 20 * 1024 * 1024);
        if ($body === null || $code >= 400 || strncmp((string) $ctype, 'image/', 6) !== 0) {
            http_response_code(502);
            echo 'not an image';
            return;
        }
        header('Content-Type: ' . $ctype);
        header('Cache-Control: public, max-age=86400');
        echo $body;
    }

    /** 사설/로컬 호스트 차단(SSRF 최소 방어). */
    private function isBlockedHost(string $host): bool
    {
        $h = strtolower($host);
        if ($h === 'localhost' || str_ends_with($h, '.local') || str_ends_with($h, '.internal')) return true;
        $ip = filter_var($h, FILTER_VALIDATE_IP) ? $h : gethostbyname($h);
        if (filter_var($ip, FILTER_VALIDATE_IP)) {
            if (!filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
                return true; // 사설/예약 IP
            }
        }
        return false;
    }

    /** @return array{0:?string,1:int,2:?string} [body, httpCode, contentType] */
    private function httpGet(string $url, int $timeout, array $headers = [], int $maxBytes = 0): array
    {
        if (function_exists('curl_init')) {
            $ch = curl_init($url);
            curl_setopt_array($ch, [
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_TIMEOUT        => $timeout,
                CURLOPT_CONNECTTIMEOUT => 6,
                CURLOPT_HTTPHEADER     => $headers,
                CURLOPT_SSL_VERIFYPEER => true,
            ]);
            // open_basedir 환경에선 FOLLOWLOCATION 사용 불가 → 가능할 때만 켜서 리다이렉트 대응.
            // 리다이렉트 hop도 https만 허용(SSRF: https→302→http://사설IP 다운그레이드 우회 차단)
            if (!ini_get('open_basedir')) {
                curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
                curl_setopt($ch, CURLOPT_MAXREDIRS, 3);
                curl_setopt($ch, CURLOPT_PROTOCOLS, CURLPROTO_HTTPS);
                curl_setopt($ch, CURLOPT_REDIR_PROTOCOLS, CURLPROTO_HTTPS);
            }
            $body = curl_exec($ch);
            $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
            $ctype = (string) curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
            curl_close($ch);
            if ($body === false) return [null, 0, null];
            if ($maxBytes > 0 && strlen((string) $body) > $maxBytes) return [null, 0, null];
            return [(string) $body, $code, $ctype];
        }
        // curl 없으면 스트림 컨텍스트
        $ctx = stream_context_create(['http' => ['timeout' => $timeout, 'header' => implode("\r\n", $headers)]]);
        $body = @file_get_contents($url, false, $ctx);
        $code = 200;
        $ctype = null;
        foreach ($http_response_header ?? [] as $hd) {
            if (stripos($hd, 'Content-Type:') === 0) $ctype = trim(substr($hd, 13));
            if (preg_match('#HTTP/\S+\s+(\d+)#', $hd, $m)) $code = (int) $m[1];
        }
        return [$body === false ? null : $body, $code, $ctype];
    }

    private function json(mixed $payload, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    }
}
