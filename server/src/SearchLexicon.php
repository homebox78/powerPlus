<?php
declare(strict_types=1);

/**
 * 검색어 정규화 + 동의어/색상/한↔영 확장 사전.
 * 자연어 질의("파란 톤 차트 아이콘")를 토큰으로 쪼개고 각 토큰을 동의어 묶음으로
 * 확장해 LIKE 매칭 적중률을 높인다. 임베딩 의미검색 도입 전의 1차 레이어.
 */
final class SearchLexicon
{
    /** 동의어 묶음 — 한 묶음 안의 단어는 서로 확장된다(양방향). 소문자로 비교. */
    private const GROUPS = [
        // 색상
        ['파랑','파란','파란색','블루','blue','남색','네이비','navy'],
        ['하늘색','하늘','스카이','sky','skyblue','연파랑'],
        ['청록','민트','틸','teal','mint','cyan','시안'],
        ['빨강','빨간','빨간색','레드','red','적색'],
        ['주황','오렌지','orange'],
        ['노랑','노란','옐로','옐로우','yellow','금색','골드','gold'],
        ['초록','녹색','그린','green'],
        ['보라','퍼플','purple','바이올렛','violet'],
        ['분홍','핑크','pink'],
        ['검정','검은','블랙','black','흑색'],
        ['흰색','하양','화이트','white'],
        ['회색','그레이','gray','grey','은색','실버','silver'],
        ['갈색','브라운','brown'],
        // 자산 유형
        ['아이콘','icon','icons','픽토그램','pictogram'],
        ['사진','포토','photo','image','이미지','사진자료'],
        ['일러스트','일러스트레이션','illustration','illust','그림','삽화'],
        ['다이어그램','diagram','도식','도표'],
        ['차트','그래프','chart','graph','그래픽','통계'],
        ['로고','logo','심볼','symbol','엠블럼'],
        ['장표','슬라이드','slide','ppt','피피티'],
        // 장표 페이지 종류
        ['표지','커버','cover','title','타이틀'],
        ['목차','차례','toc','agenda','목록'],
        ['간지','파트','part','divider','섹션','구분','전환'],
        ['인사말','greeting','인사','드리는글'],
        ['마무리','감사','맺음말','qa','클로징','closing','thankyou'],
        ['본문','콘텐츠','content','내용'],
        // 도메인/주제
        ['소상공인','자영업','small business','smb'],
        ['빅데이터','bigdata','big data','데이터','data'],
        ['데이터베이스','디비','db','database','dbms','디비베이스','데이타베이스','rdbms','sql'],
        ['클라우드','cloud','saas','iaas','paas'],
        ['서버','server','서버랙','호스트','host'],
        ['네트워크','network','통신','랜','lan','네트웍'],
        ['api','에이피아이','인터페이스','interface','rest','restful','엔드포인트','endpoint'],
        ['개발','코딩','coding','development','프로그래밍','programming','소스코드','코드','code'],
        ['백업','backup','복구','recovery','이중화'],
        ['저장소','스토리지','storage','디스크','disk','ssd'],
        ['방화벽','firewall','접근제어'],
        ['인증','로그인','login','auth','토큰','token','oauth','jwt'],
        ['화살표','arrow','arrows','방향','direction','지시'],
        ['순환','반복','loop','cycle','circular','재활용','refresh','새로고침'],
        ['흐름','플로우','flow','프로세스','process','절차','단계'],
        ['보안','security','정보보호'],
        ['인공지능','ai','에이아이','머신러닝','딥러닝','ml'],
        ['정부','공공','행정','government','public','공공기관'],
        ['모바일','mobile','앱','app','스마트폰'],
        ['바이오','bio','생명','헬스케어','healthcare'],
        ['기후','기후위기','climate','환경','친환경','탄소중립'],
        ['플랫폼','platform','시스템','system'],
        ['운영','유지관리','유지보수','operation','maintenance'],
        ['구축','개발','build','development','구현'],
        ['전략','strategy','추진전략','approach'],
        ['관리','management','관리체계'],
        ['비대면','언택트','untact','온라인','online'],
        ['바우처','voucher','지원금','지원'],
        ['건설','construction','시공','건축'],
        ['신분증','id','인증','신원확인'],
        ['제안서','제안','proposal','rfp','입찰'],
        ['패키지','package','묶음'],
        ['사업','프로젝트','project','과제'],
        ['교육','학습','training','education','연수'],
        ['의료','병원','medical','hospital','진료'],
        ['금융','은행','finance','bank','핀테크'],
        ['물류','배송','logistics','유통'],
        ['제조','공장','manufacturing','생산','스마트팩토리'],
        ['에너지','전력','energy','발전','재생에너지'],
    ];

    /**
     * 복합어 분해용 어휘(GROUPS 전 단어 + 자주 붙여 쓰는 낱말).
     * "기후위기제안서"처럼 띄어쓰기 없이 입력해도 조각으로 나눠 찾게 한다.
     */
    private const EXTRA_VOCAB = [
        '구축','운영','관리','지원','서비스','시스템','플랫폼','인프라','솔루션',
        '표지','목차','간지','본문','마무리','전략','목표','배경','추진','현황','계획',
        '기후','위기','환경','탄소','중립','데이터','분석','통계','보고','성과',
        '소상공인','공공','정부','기업','고객','사용자','국가','지자체',
    ];

    /** 카테고리 힌트: 토큰 -> category key */
    private const CAT_HINT = [
        '아이콘'=>'icon','icon'=>'icon','픽토그램'=>'icon',
        '사진'=>'photo','photo'=>'photo','이미지'=>'photo',
        '일러스트'=>'illust','illustration'=>'illust','그림'=>'illust','삽화'=>'illust',
        '다이어그램'=>'diagram','diagram'=>'diagram','도식'=>'diagram',
        '장표'=>'ppt','슬라이드'=>'ppt','ppt'=>'ppt','피피티'=>'ppt',
        '제안서'=>'ppt','제안'=>'ppt',
        '로고'=>'logo','logo'=>'logo','심볼'=>'logo',
    ];

    /** 불용어 — 검색에서 무시(의미 약함) */
    private const STOP = ['톤','느낌','스타일','색','색상','계열','분위기','종류','관련','자료','이미지를','으로','하는','있는','그','및','등','좀','적','형','용'];

    private static ?array $index = null;

    private static function buildIndex(): void
    {
        if (self::$index !== null) return;
        $idx = [];
        foreach (self::GROUPS as $g) {
            foreach ($g as $w) {
                $key = mb_strtolower(trim($w));
                $idx[$key] = array_values(array_unique(array_merge($idx[$key] ?? [], $g)));
            }
        }
        self::$index = $idx;
    }

    /** 질의 문자열 -> 정규화 토큰 배열(불용어 제거, 중복 제거). */
    public static function tokenize(string $q): array
    {
        $q = mb_strtolower(trim($q));
        $parts = preg_split('/[\s,\.\/\|\(\)\[\]"\x27]+/u', $q, -1, PREG_SPLIT_NO_EMPTY) ?: [];
        $out = [];
        foreach ($parts as $p) {
            $p = trim($p);
            if ($p === '' || mb_strlen($p) < 1) continue;
            if (in_array($p, self::STOP, true)) continue;
            // 붙여 쓴 복합어는 아는 낱말로 쪼갠다("기후위기제안서" → 기후위기 + 제안서)
            $parts = self::decompose($p);
            foreach ($parts ?: [$p] as $piece) {
                if ($piece === '' || in_array($piece, self::STOP, true)) continue;
                if (!in_array($piece, $out, true)) $out[] = $piece;
            }
        }
        return self::glue($out);
    }

    /**
     * 띄어 쓴 한 낱말을 도로 붙인다("데이터 베이스" → "데이터베이스").
     * 붙인 말이 사전에 있을 때만 합친다 — 아무 말이나 붙이면 엉뚱한 낱말이 된다.
     * 세 조각까지 본다("빅 데이터 베이스").
     */
    public static function glue(array $tokens): array
    {
        self::buildIndex();
        $known = function (string $w): bool {
            return isset(self::$index[$w]) || in_array($w, self::vocab(), true);
        };
        $out = [];
        $n = count($tokens);
        for ($i = 0; $i < $n; ) {
            $hit = null; $take = 1;
            for ($len = 3; $len >= 2; $len--) {
                if ($i + $len > $n) continue;
                $joined = mb_strtolower(implode('', array_slice($tokens, $i, $len)));
                if ($known($joined)) { $hit = $joined; $take = $len; break; }
            }
            $out[] = $hit ?? $tokens[$i];
            $i += $take;
        }
        return array_values(array_unique($out));
    }

    /** 분해용 어휘 목록(길이 내림차순) — 최장일치 우선. */
    private static ?array $vocab = null;

    private static function vocab(): array
    {
        if (self::$vocab !== null) return self::$vocab;
        $words = self::EXTRA_VOCAB;
        foreach (self::GROUPS as $g) foreach ($g as $w) $words[] = $w;
        $words = array_values(array_unique(array_map(fn($w) => mb_strtolower(trim($w)), $words)));
        $words = array_values(array_filter($words, fn($w) => mb_strlen($w) >= 2 && !str_contains($w, ' ')));
        usort($words, fn($a, $b) => mb_strlen($b) <=> mb_strlen($a)); // 긴 낱말 먼저
        self::$vocab = $words;
        return self::$vocab;
    }

    /**
     * 띄어쓰기 없는 복합어를 아는 낱말로 쪼갠다(최장일치).
     * "기후위기제안서" → ['기후위기','제안서'] · 분해 실패 시 빈 배열(원문 그대로 쓰라는 뜻).
     * 어휘에 없는 구간은 2글자 이상일 때만 조각으로 남긴다(1글자 노이즈 방지).
     */
    public static function decompose(string $token): array
    {
        self::buildIndex();
        $t = mb_strtolower(trim($token));
        if (mb_strlen($t) < 4) return [];          // 짧은 말은 쪼갤 이유가 없다
        if (isset(self::$index[$t])) return [];    // 사전에 그대로 있는 말은 두 번 나누지 않는다

        $parts = [];
        $buf = '';
        $i = 0;
        $len = mb_strlen($t);
        $matched = false;
        while ($i < $len) {
            $hit = null;
            foreach (self::vocab() as $w) {
                $wl = mb_strlen($w);
                if ($wl <= $len - $i && mb_substr($t, $i, $wl) === $w) { $hit = $w; break; }
            }
            if ($hit !== null) {
                if (mb_strlen($buf) >= 2) $parts[] = $buf;
                $buf = '';
                $parts[] = $hit;
                $i += mb_strlen($hit);
                $matched = true;
            } else {
                $buf .= mb_substr($t, $i, 1);
                $i++;
            }
        }
        if (mb_strlen($buf) >= 2) $parts[] = $buf;

        // 아는 낱말이 하나도 없으면 분해로 볼 수 없다(엉뚱한 조각 방지)
        if (!$matched || count($parts) < 2) return [];
        return array_values(array_unique($parts));
    }

    /** 토큰 -> 동의어 확장 집합(자기 자신 포함). */
    public static function expand(string $token): array
    {
        self::buildIndex();
        $t = mb_strtolower(trim($token));
        $set = self::$index[$t] ?? [$t];
        if (!in_array($t, $set, true)) $set[] = $t;
        return array_values(array_unique($set));
    }

    // ───────────────────────── 오타 교정 ─────────────────────────
    // 사용자는 "코드"를 "코ㅡㄷ"·"코그"처럼 자모가 밀리거나 바뀐 채로 친다.
    // 자산마다 오타 태그를 저장하는 대신, 검색어를 자모로 풀어 실제 태그와 대조해 고친다
    // (데이터가 안 늘고, 앞으로 등록되는 자산에도 그대로 적용된다).

    private const CHO = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'];
    private const JUNG = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ'];
    private const JONG = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'];

    /** 한글을 자모 배열로 푼다("코드" → ㅋ ㅗ ㄷ ㅡ). 한글이 아니면 글자 그대로. */
    public static function jamo(string $s): array
    {
        $out = [];
        $len = mb_strlen($s);
        for ($i = 0; $i < $len; $i++) {
            $ch = mb_substr($s, $i, 1);
            $code = mb_ord($ch, 'UTF-8');
            if ($code >= 0xAC00 && $code <= 0xD7A3) {
                $n = $code - 0xAC00;
                $out[] = self::CHO[intdiv($n, 588)];
                $out[] = self::JUNG[intdiv($n % 588, 28)];
                $j = self::JONG[$n % 28];
                if ($j !== '') $out[] = $j;
            } else {
                $out[] = $ch;
            }
        }
        return $out;
    }

    /** 자모 편집거리(글자 바뀜·빠짐·더해짐 + 앞뒤 뒤바뀜까지 1로 센다). */
    private static function dist(array $a, array $b, int $cap): int
    {
        $la = count($a); $lb = count($b);
        if (abs($la - $lb) > $cap) return $cap + 1;
        $prev2 = []; $prev = range(0, $lb); $cur = [];
        for ($i = 1; $i <= $la; $i++) {
            $cur = [$i];
            $best = $i;
            for ($j = 1; $j <= $lb; $j++) {
                $cost = ($a[$i - 1] === $b[$j - 1]) ? 0 : 1;
                $v = min($prev[$j] + 1, $cur[$j - 1] + 1, $prev[$j - 1] + $cost);
                // 뒤바뀜("ㄷㅡ" ↔ "ㅡㄷ")도 한 번의 실수로 센다
                if ($i > 1 && $j > 1 && $a[$i - 1] === $b[$j - 2] && $a[$i - 2] === $b[$j - 1]) {
                    $v = min($v, $prev2[$j - 2] + 1);
                }
                $cur[$j] = $v;
                if ($v < $best) $best = $v;
            }
            if ($best > $cap) return $cap + 1;   // 더 볼 것도 없음
            $prev2 = $prev; $prev = $cur;
        }
        return $prev[$lb];
    }

    private static ?array $tagDict = null;

    /**
     * 교정 후보 낱말 사전 = 실제 등록된 태그 + 동의어 사전.
     * 태그는 매번 훑기 무거워서 하루 단위로 파일에 캐시한다(실패해도 사전만으로 동작).
     */
    private static function dict(): array
    {
        if (self::$tagDict !== null) return self::$tagDict;
        $words = [];
        foreach (self::vocab() as $w) $words[$w] = 100;   // 사전 낱말은 기본 가중

        $cache = rtrim(sys_get_temp_dir(), '/\\') . '/pp_tagdict.json';
        $fresh = is_readable($cache) && (time() - (int) @filemtime($cache) < 86400);
        $tags = null;
        if ($fresh) {
            $raw = @file_get_contents($cache);
            $tags = $raw ? json_decode($raw, true) : null;
        }
        if (!is_array($tags)) {
            $tags = [];
            try {
                $st = Database::pdo()->query('SELECT tags FROM assets WHERE tags IS NOT NULL');
                while (($t = $st->fetchColumn()) !== false) {
                    foreach ((json_decode((string) $t, true) ?: []) as $w) {
                        $w = mb_strtolower(trim((string) $w));
                        if ($w === '' || mb_strlen($w) < 2 || mb_strlen($w) > 10) continue;
                        $tags[$w] = ($tags[$w] ?? 0) + 1;
                    }
                }
                $tags = array_filter($tags, fn($n) => $n >= 2);   // 한 번뿐인 태그는 오타일 수도
                @file_put_contents($cache, json_encode($tags, JSON_UNESCAPED_UNICODE));
            } catch (\Throwable $e) {
                $tags = [];   // DB를 못 읽어도 사전만으로 교정은 된다
            }
        }
        foreach ($tags as $w => $n) $words[$w] = ($words[$w] ?? 0) + (int) $n;

        self::$tagDict = $words;
        return self::$tagDict;
    }

    /**
     * 오타로 보이는 낱말을 실제 낱말로 고친다. 고칠 게 없으면 null.
     * 사전에 이미 있는 말은 건드리지 않는다(멀쩡한 검색어를 바꾸면 더 나쁘다).
     */
    public static function correct(string $token): ?string
    {
        $t = mb_strtolower(trim($token));
        $len = mb_strlen($t);
        if ($len < 2 || $len > 10) return null;

        $dict = self::dict();
        if (isset($dict[$t])) return null;              // 아는 말 = 오타 아님

        $tj = self::jamo($t);
        $cap = $len <= 3 ? 1 : 2;                        // 짧은 말일수록 엄격하게
        $best = null; $bestD = $cap + 1; $bestN = 0;
        foreach ($dict as $w => $n) {
            $wl = mb_strlen((string) $w);
            if (abs($wl - $len) > 1) continue;           // 길이가 많이 다르면 다른 말
            $wj = self::jamo((string) $w);
            if (abs(count($wj) - count($tj)) > $cap) continue;
            $d = self::dist($tj, $wj, $cap);
            if ($d > $cap) continue;
            if ($d < $bestD || ($d === $bestD && $n > $bestN)) { $best = (string) $w; $bestD = $d; $bestN = $n; }
        }
        return $best;
    }

    /**
     * 토큰 목록을 훑어 오타를 고친다. [고친 토큰들, 원본=>교정 대응표] 반환.
     * 대응표는 화면에 "‘코드’로 검색했어요"를 보여주기 위한 것.
     */
    public static function correctTokens(array $tokens): array
    {
        $out = []; $fixed = [];
        foreach ($tokens as $t) {
            $c = self::correct($t);
            if ($c !== null && $c !== $t) { $fixed[$t] = $c; $out[] = $c; }
            else $out[] = $t;
        }
        return [array_values(array_unique($out)), $fixed];
    }

    /** 토큰들 중 카테고리를 가리키는 것이 있으면 그 category key 들을 반환. */
    public static function categoryHints(array $tokens): array
    {
        $hits = [];
        foreach ($tokens as $t) {
            $t = mb_strtolower($t);
            if (isset(self::CAT_HINT[$t])) $hits[self::CAT_HINT[$t]] = true;
        }
        return array_keys($hits);
    }
}
