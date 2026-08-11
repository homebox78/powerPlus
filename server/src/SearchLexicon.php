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
        ['클라우드','cloud','saas'],
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
        return $out;
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
