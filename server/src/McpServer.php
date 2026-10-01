<?php
declare(strict_types=1);

require_once __DIR__ . '/AssetService.php';
require_once __DIR__ . '/CategoryService.php';
require_once __DIR__ . '/McpKeyService.php';

/**
 * powerPlus MCP 서버 — Streamable HTTP(무상태) 를 PHP 하나로 구현.
 *
 * 왜 SDK 없이 PHP 인가:
 *   MCP Streamable HTTP 는 "POST 로 JSON-RPC 를 받아 JSON 으로 돌려주는 것"이 전부다(서버가 먼저
 *   말을 거는 기능을 안 쓰면 SSE 도 필요 없다). 그래서 Node 상주 프로세스·systemd 없이 기존 PHP API
 *   옆에 엔드포인트 하나로 붙였다 — 서버를 옮겨도 Apache+PHP 만 있으면 그대로 따라간다.
 *
 * 흐름: POST /mcp (Authorization: Bearer pp_mcp_…)
 *   initialize → tools/list → tools/call  (알림(notification)은 202 빈 응답)
 * 데이터는 애드인과 같은 AssetService 를 직접 호출한다(HTTP 왕복 없음, 검색 품질 동일).
 */
final class McpServer
{
    private const VERSIONS = ['2025-06-18', '2025-03-26', '2024-11-05'];
    private const SERVER = ['name' => 'powerplus', 'title' => 'powerPlus 자산 라이브러리', 'version' => '1.0.0'];

    private const INSTRUCTIONS = <<<TXT
powerPlus — 제안서·발표 장표용 디자인 자산 라이브러리(아이콘·사진·일러스트·다이어그램·로고·장표).

쓰는 순서:
1) list_categories 로 카테고리와 수량을 본다.
2) search_assets 로 찾는다. query 는 한국어·영어 낱말 모두 된다(동의어·오타 교정·띄어쓰기 보정 포함).
   카테고리를 알면 category 를 꼭 준다. 결과가 많으면 list_topics 의 topic 으로 좁힌다.
3) 후보는 get_asset 으로 썸네일을 직접 보고 고른다(제목·태그만으로 고르지 말 것).
4) 같은 톤으로 여러 개가 필요하면 style_set(같은 스타일 묶음), 비슷한 것을 더 보려면 similar_assets.

결과의 image_url 이 원본(문서·슬라이드 삽입용, 원본 해상도), thumb_url 은 미리보기용이다.
장표(ppt) 자산은 slide_url 이 .pptx 원본이며, slide_kind(package=제안서 묶음/single=낱장)와
slide_page(cover·toc·divider·content·qa·etc)로 용도를 구분한다.
TXT;

    private AssetService $assets;
    private ?array $key = null;

    public function __construct()
    {
        $this->assets = new AssetService();
    }

    /** 요청 하나를 처리하고 응답을 내보낸다. $bearer 는 Authorization 헤더 값(없으면 null). */
    public function handle(string $method, ?string $bearer): void
    {
        header('Cache-Control: no-store');

        if ($method === 'GET') {
            // 서버가 먼저 보내는 스트림(SSE)은 제공하지 않는다 — 스펙상 405 로 알린다.
            http_response_code(405);
            header('Allow: POST');
            return;
        }
        if ($method === 'DELETE') {
            http_response_code(204); // 세션을 두지 않으므로 종료할 것도 없다
            return;
        }
        if ($method !== 'POST') {
            http_response_code(405);
            header('Allow: POST');
            return;
        }

        $this->key = $bearer ? (new McpKeyService())->verify($bearer) : null;
        if ($this->key === null) {
            http_response_code(401);
            header('WWW-Authenticate: Bearer realm="powerPlus MCP"');
            $this->send(['jsonrpc' => '2.0', 'id' => null,
                'error' => ['code' => -32001, 'message' => 'MCP 키가 없거나 유효하지 않습니다. 관리자 화면 > MCP 연동에서 발급받은 키를 Authorization: Bearer 로 보내세요.']]);
            return;
        }

        $raw = file_get_contents('php://input') ?: '';
        $msg = json_decode($raw, true);
        if (!is_array($msg)) {
            $this->send(self::err(null, -32700, 'Parse error'));
            return;
        }

        // 배치(배열)와 단건 모두 받는다. 요청(id 있음)만 응답하고, 알림만 왔으면 202.
        $isBatch = array_is_list($msg);
        $items = $isBatch ? $msg : [$msg];
        $out = [];
        foreach ($items as $m) {
            $r = $this->dispatch(is_array($m) ? $m : []);
            if ($r !== null) $out[] = $r;
        }
        if (!$out) {
            http_response_code(202);
            return;
        }
        $this->send($isBatch ? $out : $out[0]);
    }

    private function dispatch(array $m): ?array
    {
        $id = $m['id'] ?? null;
        $isNotification = !array_key_exists('id', $m);
        $method = (string) ($m['method'] ?? '');
        $params = is_array($m['params'] ?? null) ? $m['params'] : [];

        if (($m['jsonrpc'] ?? '') !== '2.0' || $method === '') {
            return $isNotification ? null : self::err($id, -32600, 'Invalid Request');
        }
        if ($isNotification) return null; // notifications/initialized 등

        try {
            switch ($method) {
                case 'initialize':
                    $want = (string) ($params['protocolVersion'] ?? '');
                    return self::ok($id, [
                        'protocolVersion' => in_array($want, self::VERSIONS, true) ? $want : self::VERSIONS[0],
                        'capabilities'    => ['tools' => ['listChanged' => false]],
                        'serverInfo'      => self::SERVER,
                        'instructions'    => self::INSTRUCTIONS,
                    ]);
                case 'ping':
                    return self::ok($id, (object) []);
                case 'tools/list':
                    return self::ok($id, ['tools' => $this->tools()]);
                case 'tools/call':
                    return self::ok($id, $this->call((string) ($params['name'] ?? ''), is_array($params['arguments'] ?? null) ? $params['arguments'] : []));
                case 'resources/list':
                    return self::ok($id, ['resources' => []]);
                case 'prompts/list':
                    return self::ok($id, ['prompts' => []]);
                default:
                    return self::err($id, -32601, "Method not found: $method");
            }
        } catch (InvalidArgumentException $e) {
            return self::err($id, -32602, $e->getMessage());
        } catch (Throwable $e) {
            error_log('[powerPlus mcp] ' . $e->getMessage() . ' @ ' . $e->getFile() . ':' . $e->getLine());
            return self::err($id, -32603, 'Internal error');
        }
    }

    /* ───────────────────────── 도구 정의 ───────────────────────── */

    private function tools(): array
    {
        $cats = array_map(static fn($c) => (string) $c['key'], (new CategoryService())->all());
        $ro = ['readOnlyHint' => true, 'openWorldHint' => false];
        $idProp = ['type' => 'string', 'description' => '자산 id (예: icon_1043, photo_566, ppt_682)'];
        return [
            [
                'name' => 'search_assets',
                'title' => '자산 검색',
                'description' => '키워드로 자산을 찾는다. 한국어·영어 모두 되고, 동의어·오타·띄어쓰기를 보정한다. query 를 비우면 최신순 목록.',
                'inputSchema' => ['type' => 'object', 'properties' => [
                    'query'    => ['type' => 'string', 'description' => '검색어 (예: "기후위기 아이콘", "악수 일러스트", "handshake")'],
                    'category' => ['type' => 'string', 'enum' => array_merge(['all'], $cats), 'description' => '카테고리로 제한(기본 all)'],
                    'topic'    => ['type' => 'string', 'description' => 'list_topics 로 얻은 주제 key 로 더 좁힌다'],
                    'slide_kind' => ['type' => 'string', 'enum' => ['package', 'single'], 'description' => '장표만: 묶음(package)/낱장(single)'],
                    'slide_page' => ['type' => 'string', 'enum' => ['cover', 'toc', 'divider', 'content', 'greeting', 'qa', 'etc'], 'description' => '장표 낱장의 페이지 종류'],
                    'sort'     => ['type' => 'string', 'enum' => ['latest', 'popular', 'name', 'favorites'], 'description' => '정렬(검색어가 있으면 관련도 우선)'],
                    'page'     => ['type' => 'integer', 'minimum' => 1, 'default' => 1],
                    'limit'    => ['type' => 'integer', 'minimum' => 1, 'maximum' => 50, 'default' => 20],
                ]],
                'annotations' => $ro,
            ],
            [
                'name' => 'get_asset',
                'title' => '자산 상세 + 미리보기',
                'description' => 'id 로 자산 하나의 정보(원본 URL·태그·장표 파일)와 썸네일 이미지를 돌려준다. 고르기 전에 그림을 직접 확인할 때 쓴다.',
                'inputSchema' => ['type' => 'object', 'required' => ['id'], 'properties' => [
                    'id' => $idProp,
                    'preview' => ['type' => 'boolean', 'default' => true, 'description' => 'false 면 이미지 없이 정보만'],
                ]],
                'annotations' => $ro,
            ],
            [
                'name' => 'similar_assets',
                'title' => '비슷한 자산',
                'description' => '태그가 많이 겹치는 자산을 추천한다(같은 카테고리 우선).',
                'inputSchema' => ['type' => 'object', 'required' => ['id'], 'properties' => [
                    'id' => $idProp,
                    'limit' => ['type' => 'integer', 'minimum' => 1, 'maximum' => 50, 'default' => 12],
                ]],
                'annotations' => $ro,
            ],
            [
                'name' => 'style_set',
                'title' => '같은 스타일 묶음',
                'description' => '같은 시기에 같은 톤(색감·화풍)으로 만든 자산 묶음. 한 장표에 톤을 맞춰 여러 개 넣을 때 쓴다.',
                'inputSchema' => ['type' => 'object', 'required' => ['id'], 'properties' => [
                    'id' => $idProp,
                    'page' => ['type' => 'integer', 'minimum' => 1, 'default' => 1],
                    'limit' => ['type' => 'integer', 'minimum' => 1, 'maximum' => 120, 'default' => 40],
                ]],
                'annotations' => $ro,
            ],
            [
                'name' => 'list_categories',
                'title' => '카테고리 목록',
                'description' => '카테고리 key·이름·자산 수.',
                'inputSchema' => ['type' => 'object', 'properties' => (object) []],
                'annotations' => $ro,
            ],
            [
                'name' => 'list_topics',
                'title' => '카테고리 안 주제',
                'description' => '카테고리 안의 세부 주제(예: 아이콘 > 업무·서버·기후)와 자산 수. search_assets 의 topic 으로 쓴다.',
                'inputSchema' => ['type' => 'object', 'required' => ['category'], 'properties' => [
                    'category' => ['type' => 'string', 'enum' => $cats],
                ]],
                'annotations' => $ro,
            ],
            [
                'name' => 'suggest_keywords',
                'title' => '검색어 추천',
                'description' => '실제 등록된 태그에서 검색어를 추천한다. query 가 비면 최근 인기 검색어. 무엇으로 찾을지 막막할 때 쓴다.',
                'inputSchema' => ['type' => 'object', 'properties' => [
                    'query' => ['type' => 'string'],
                    'limit' => ['type' => 'integer', 'minimum' => 1, 'maximum' => 12, 'default' => 8],
                ]],
                'annotations' => $ro,
            ],
        ];
    }

    /* ───────────────────────── 도구 실행 ───────────────────────── */

    private function call(string $name, array $a): array
    {
        switch ($name) {
            case 'search_assets':
                $limit = self::int($a, 'limit', 20, 1, 50);
                $page = self::int($a, 'page', 1, 1, 10000);
                $r = $this->assets->list(
                    (string) ($a['category'] ?? 'all') ?: 'all',
                    trim((string) ($a['query'] ?? '')),
                    $page, $limit,
                    (string) ($a['sort'] ?? 'latest') ?: 'latest',
                    (string) ($a['slide_kind'] ?? ''),
                    (string) ($a['slide_page'] ?? ''),
                    (string) ($a['topic'] ?? '')
                );
                $this->logSearch((string) ($a['query'] ?? ''), (string) ($a['category'] ?? 'all'), (int) ($r['total'] ?? 0), $page);
                return self::result([
                    'total' => (int) $r['total'], 'page' => $page, 'limit' => $limit,
                    'corrected' => $r['corrected'] ?? null,
                    'assets' => array_map([self::class, 'brief'], $r['data']),
                ]);

            case 'get_asset':
                $id = self::requireId($a);
                $asset = $this->assets->find($id);
                if ($asset === null) return self::toolError("자산을 찾을 수 없습니다: $id");
                $this->logUse($id);
                $data = self::full($asset);
                $content = [['type' => 'text', 'text' => json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)]];
                if (($a['preview'] ?? true) !== false) {
                    $img = self::thumbImage($asset);
                    if ($img) $content[] = $img;
                }
                return ['content' => $content, 'structuredContent' => $data];

            case 'similar_assets':
                $r = $this->assets->similar(self::requireId($a), self::int($a, 'limit', 12, 1, 50));
                return self::result(['assets' => array_map([self::class, 'brief'], $r['data'])]);

            case 'style_set':
                $r = $this->assets->styleSet(self::requireId($a), self::int($a, 'page', 1, 1, 10000), self::int($a, 'limit', 40, 1, 120));
                return self::result([
                    'total' => (int) ($r['total'] ?? 0), 'page' => (int) ($r['page'] ?? 1),
                    'assets' => array_map([self::class, 'brief'], $r['data']),
                ]);

            case 'list_categories':
                return self::result(['categories' => array_map(
                    static fn($c) => ['key' => $c['key'], 'label' => $c['label'], 'count' => (int) $c['count']],
                    (new CategoryService())->allWithCounts()
                )]);

            case 'list_topics':
                $cat = trim((string) ($a['category'] ?? ''));
                if ($cat === '') throw new InvalidArgumentException('category 가 필요합니다');
                return self::result(['category' => $cat, 'topics' => $this->assets->topicCounts($cat)]);

            case 'suggest_keywords':
                return self::result(['keywords' => $this->assets->suggest(
                    trim((string) ($a['query'] ?? '')), self::int($a, 'limit', 8, 1, 12)
                )]);
        }
        throw new InvalidArgumentException("알 수 없는 도구: $name");
    }

    /* ───────────────────────── 모양 다듬기 ───────────────────────── */

    /** 목록용 — 모델 컨텍스트를 아끼려고 태그는 앞 10개만. */
    private static function brief(array $x): array
    {
        $o = [
            'id' => $x['id'],
            'category' => $x['category'],
            'name' => $x['name'] ?: null,
            'tags' => array_slice(array_merge($x['tags_ko'] ?? [], array_slice($x['tags_en'] ?? [], 0, 3)), 0, 10),
            'thumb_url' => $x['thumb_url'],
            'image_url' => $x['image_url'],
        ];
        if (!empty($x['slide_url'])) {
            $o['slide_url'] = $x['slide_url'];
            $o['slide_kind'] = $x['slide_kind'] ?? null;
            $o['slide_page'] = $x['slide_page'] ?? null;
        }
        return $o;
    }

    private static function full(array $x): array
    {
        $o = self::brief($x);
        unset($o['tags']);
        $o['tags_ko'] = $x['tags_ko'] ?? [];
        $o['tags_en'] = $x['tags_en'] ?? [];
        $p = __DIR__ . '/../' . ltrim((string) ($x['image_path'] ?? ''), '/');
        if (!empty($x['image_path']) && is_file($p) && ($s = @getimagesize($p))) {
            $o['width'] = $s[0];
            $o['height'] = $s[1];
        }
        return $o;
    }

    /** 썸네일 파일을 MCP image content 로 — 모델이 그림을 직접 보고 고르게. 1.5MB 넘으면 생략. */
    private static function thumbImage(array $x): ?array
    {
        $rel = (string) (($x['thumb_path'] ?? '') ?: ($x['image_path'] ?? ''));
        if ($rel === '') return null;
        $p = __DIR__ . '/../' . ltrim($rel, '/');
        if (!is_file($p) || filesize($p) > 1_500_000) return null;
        $mime = match (strtolower(pathinfo($p, PATHINFO_EXTENSION))) {
            'png' => 'image/png', 'jpg', 'jpeg' => 'image/jpeg', 'webp' => 'image/webp', 'gif' => 'image/gif',
            default => null,
        };
        if ($mime === null) return null;
        return ['type' => 'image', 'data' => base64_encode((string) file_get_contents($p)), 'mimeType' => $mime];
    }

    /* ───────────────────────── 기록 ───────────────────────── */

    /** 검색 로그 — 애드인과 같은 search_logs 에 'mcp:<키 이름>' 으로 남겨 무결과율·수요에 합산. */
    private function logSearch(string $q, string $cat, int $n, int $page): void
    {
        if (trim($q) === '' || $page !== 1) return;
        try {
            Database::pdo()->prepare(
                'INSERT INTO search_logs (email, query, category, results, searched_at) VALUES (:e, :q, :c, :n, NOW())'
            )->execute([':e' => $this->who(), ':q' => mb_substr(trim($q), 0, 255), ':c' => $cat ?: 'all', ':n' => $n]);
        } catch (Throwable $e) { /* 무시 */ }
    }

    /** 자산을 열어본 것을 사용 기록으로 — 인기 순위에 MCP 사용분도 반영된다. */
    private function logUse(string $id): void
    {
        try {
            Database::pdo()->prepare('INSERT INTO usage_log (asset_id, email, used_at) VALUES (:a, :e, NOW())')
                ->execute([':a' => $id, ':e' => $this->who()]);
        } catch (Throwable $e) { /* 무시 */ }
    }

    private function who(): string
    {
        return mb_substr('mcp:' . ($this->key['name'] ?? '?'), 0, 255);
    }

    /* ───────────────────────── JSON-RPC 도우미 ───────────────────────── */

    private static function result(array $data): array
    {
        return [
            'content' => [['type' => 'text', 'text' => json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)]],
            'structuredContent' => $data,
        ];
    }

    private static function toolError(string $msg): array
    {
        return ['content' => [['type' => 'text', 'text' => $msg]], 'isError' => true];
    }

    private static function requireId(array $a): string
    {
        $id = trim((string) ($a['id'] ?? ''));
        if ($id === '') throw new InvalidArgumentException('id 가 필요합니다');
        return $id;
    }

    private static function int(array $a, string $k, int $def, int $min, int $max): int
    {
        $v = isset($a[$k]) ? (int) $a[$k] : $def;
        return max($min, min($max, $v ?: $def));
    }

    private static function ok(mixed $id, mixed $result): array
    {
        return ['jsonrpc' => '2.0', 'id' => $id, 'result' => $result];
    }

    private static function err(mixed $id, int $code, string $message): array
    {
        return ['jsonrpc' => '2.0', 'id' => $id, 'error' => ['code' => $code, 'message' => $message]];
    }

    private function send(array $payload): void
    {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    }
}
