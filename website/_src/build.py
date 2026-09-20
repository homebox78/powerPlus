# -*- coding: utf-8 -*-
"""powerPlus 사이트 빌더 — 공유 셸 + 페이지별 본문."""
import io, os

ICONS = [1551,1553,1555,1557,1559,1561,1563,1565,1567,1569,1571,1573,1575,1577,1579,1581]
# 9열 × 8행. 드리프트가 2행(-204px)이므로 18타일 주기로 반복해야 이음매가 없다.
WALL = ''.join('<div class="wt"><img src="img/icon_%d.png" alt="" loading="lazy" width="60" height="60"></div>'
               % ICONS[(i % 18) % 16] for i in range(72))

CHECK = ('<svg class="ck" width="13" height="13" viewBox="0 0 14 14" fill="none" aria-hidden="true">'
         '<path d="M2.5 7.2 5.6 10.3 11.5 3.9" stroke="currentColor" stroke-width="1.5" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg>')
CROSS = ('<svg class="cx" width="13" height="13" viewBox="0 0 14 14" fill="none" aria-hidden="true">'
         '<path d="M3.6 3.6l6.8 6.8M10.4 3.6l-6.8 6.8" stroke="currentColor" stroke-width="1.5" '
         'stroke-linecap="round"/></svg>')

CSS = r"""
  @font-face{
    font-family:"Spoqa Han Sans Neo";
    src:url("spoqa-400.woff2") format("woff2");
    font-weight:400; font-style:normal; font-display:swap;
  }
  @font-face{
    font-family:"Spoqa Han Sans Neo";
    src:url("spoqa-500.woff2") format("woff2");
    font-weight:500; font-style:normal; font-display:swap;
  }
  @font-face{
    font-family:"Spoqa Han Sans Neo";
    src:url("spoqa-700.woff2") format("woff2");
    font-weight:700; font-style:normal; font-display:swap;
  }
:root{
    --paper:#FFFFFF;
    --panel:#F1F1F0;    /* 덱 캔버스 - 중성 라이트 그레이 */
    --ink:#1A1A1C;
    --ink-2:#63666B;
    --ink-3:#9A9DA3;
    --hair:#E8E9EB;
    --line:#DCDEE1;
    --accent:#C43E1C;   /* 강조 - 텍스트/보더. 흰 배경 대비 5.18:1 (AA) */
    --accent-b:#DD4F1E; /* 그래픽 전용 밝은 오렌지 - 진행 바/막대/글로우 */
    --brand:#E0701F;
    --page:1240px;      /* 헤어라인 폭 — 안쪽 콘텐츠가 nextsaas 와 같은 1140 이 되게 */
    --prose:720px;      /* 가운데 정렬 본문 */
    --pad:50px;
    --ink-t:#1A1A1C;    /* 제목색 */
    --ink-d:#55585E;    /* 설명글색 */
    --rule:#1A1A1C;     /* 덱 헤더 괘선 */
    --tint:#FBEEE4;     /* 라벨 pill 배경 — 브랜드 소프트 */
    --dark:#1D2026;     /* 덱 마무리 장 - 근검정 */
    --f:"Spoqa Han Sans Neo","Spoqa Han Sans","Apple SD Gothic Neo","Malgun Gothic",system-ui,-apple-system,sans-serif;
  }
  *{box-sizing:border-box;}
  body{background:var(--paper);color:var(--ink);font-family:var(--f);font-size:16px;line-height:1.75;
    -webkit-font-smoothing:antialiased;word-break:keep-all;overflow-wrap:break-word;}
  h1,h2,h3,h4{margin:0;font-weight:400;letter-spacing:-.02em;line-height:1.1;color:var(--ink-t);
    text-wrap:balance;}
  h1 b,h2 b{font-weight:700;letter-spacing:-.028em;}
  p{margin:0;}
  ul{margin:0;padding:0;list-style:none;}
  a{color:inherit;}
  img{display:block;max-width:100%;}
  :focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:6px;}

  /* ── 프레임: 풀블리드 밴드 + 세로 헤어라인 컨테이너 ────────── */
  /* 섹션 구분 — i-bricks .line-top: 양 끝이 투명해지는 2px 그라데이션 */
  .band{position:relative;}
  /* 덱은 페이드 없이 끝까지 가는 곧은 괘선으로 장을 나눈다 */
  .band::before{content:"";position:absolute;left:0;right:0;top:0;height:1px;pointer-events:none;
    background:rgba(26,26,28,.16);}
  .band--plain::before{content:none;}
  /* nextsaas 처럼 섹션 배경을 흰색 ↔ 연회색으로 번갈아 */
  main > .band:nth-of-type(even):not(.band--plain){background:var(--panel);}
  .frame{max-width:var(--page);margin:0 auto;padding:110px var(--pad);
    border-left:1px solid var(--hair);border-right:1px solid var(--hair);}
  .frame--tight{padding-top:64px;padding-bottom:64px;}
  .frame--flush{padding-left:0;padding-right:0;}
  .inner{padding-inline:var(--pad);}
  .prose{max-width:var(--prose);margin:0 auto;text-align:center;}

  /* ── 버튼 ─────────────────────────────────────────────── */
  .btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;font:inherit;font-size:14px;
    font-weight:500;text-decoration:none;white-space:nowrap;height:43px;padding:0 20px;border-radius:999px;
    border:1px solid transparent;cursor:pointer;transition:background .18s,border-color .18s,color .18s;}
  .btn--lg{height:54px;padding:0 32px;font-size:16px;}   /* 히어로 CTA */
  .btn--d{background:var(--ink);color:#fff;}
  .btn--d:hover{background:#303033;}
  .btn--s{background:#fff;color:var(--ink);border-color:var(--line);}
  .btn--s:hover{border-color:#B9BCC1;}
  .btn--sm{height:36px;padding:0 14px;font-size:14px;font-weight:500;}
  .eyebrow{display:inline-flex;align-items:center;gap:5px;color:var(--accent);font-size:13px;font-weight:500;
    text-decoration:none;letter-spacing:.01em;}
  .eyebrow:hover{text-decoration:underline;text-underline-offset:3px;}
  /* nextsaas 섹션 라벨 — 14px/500, radius full, padding 6px 20px, 연한 틴트 */
  /* 덱 eyebrow - 오렌지 1px 보더 / 투명 배경 / 대문자 / 넓은 자간 */
  .kicker{display:inline-flex;align-items:center;height:31px;padding:0 15px;border-radius:3px;
    background:transparent;border:1px solid var(--accent);color:var(--accent);
    font-size:12px;font-weight:500;line-height:1;
    letter-spacing:.14em;text-transform:uppercase;}

  /* ── 내비 ─ 하늘 위에서는 투명, 스크롤하면 흰 바 ─────────── */
  /* 서브페이지 — aside 와 같이 상단 고정 + 흰 배경 */
  .nav{position:sticky;top:0;left:0;z-index:50;width:100%;background:var(--paper);}
  .nav__in{width:100%;padding:0 16px;height:56px;display:flex;align-items:center;}
  /* 홈 — 하늘 카드 안에 얹혀 같이 스크롤된다 (aside 홈은 sticky 가 아니다) */
  .skycard .nav{position:relative;z-index:30;background:transparent;}
  .brand{display:flex;align-items:center;gap:9px;text-decoration:none;}
  .brand__m{width:25px;height:25px;border-radius:7px;display:grid;place-items:center;
    background:linear-gradient(145deg,#F0894C,#C43E1C);}
  .brand__t{font-size:17.5px;font-weight:500;letter-spacing:-.025em;}
  .nav__l{position:absolute;left:50%;transform:translateX(-50%);display:flex;gap:40px;font-size:14px;
    font-weight:500;color:#3E4145;}
  .nav__l a{text-decoration:none;}
  .nav__l a:hover,.nav__l a.on{color:var(--ink);}
  .nav__r{margin-left:auto;display:flex;align-items:center;gap:10px;}

  /* ── 히어로 ────────────────────────────────────────────── */
  /* 하늘은 뷰포트 풀블리드가 아니라 16px 안쪽으로 들어간 라운드 카드다.
     내비와 스크린샷이 전부 이 카드 안에 들어가고, 카드가 스크린샷 아래를 잘라낸다. */
  .skywrap{padding:16px 16px 0;}
  /* nextsaas 히어로처럼 부드러운 메시 그라데이션 — 이미지 0바이트, 저작권 문제 없음.
     레퍼런스는 특정 색이 튀지 않고 넓게 번지는 파스텔 워시라 알파를 낮게 잡는다. */
  /* 덱 표지 - 중성 라이트 그레이 캔버스에 오렌지 워시 한 겹 */
  .skycard{position:relative;overflow:hidden;border-radius:14px;
    background:
      radial-gradient(70% 58% at 8% 0%,  rgba(221,79,30,.10) 0%, rgba(221,79,30,0) 62%),
      radial-gradient(60% 50% at 96% 8%, rgba(221,79,30,.06) 0%, rgba(221,79,30,0) 60%),
      linear-gradient(180deg,#F4F3F1 0%,#F7F7F6 46%,#FFFFFF 100%);
    box-shadow:0 1px 0 rgba(26,26,28,.10),0 24px 46px -30px rgba(26,26,28,.30);}
  /* 덱 최상단 오렌지 진행 바 */
  .skycard::before{content:"";position:absolute;left:0;top:0;height:4px;width:34%;z-index:40;
    background:linear-gradient(90deg,var(--accent),var(--accent-b));}
  /* 덱 헤더 괘선 - 내비 아래 검정 실선 */
  .skycard .nav{border-bottom:1px solid var(--rule);margin:0 16px;}

  .hero{text-align:center;padding:64px 16px;position:relative;z-index:1;}
  /* gcar .text-block .title — 5.2rem / 800 / lh150% */
  .hero h1{font-size:34px;font-weight:400;line-height:1.1;margin:0;}
  /* gcar .title + .desc — margin-top 3.2rem, desc 2rem / 400 / lh150% */
  .hero .sub{margin:22px auto 0;max-width:50ch;font-size:16px;line-height:1.6;
    color:var(--ink-d);font-weight:400;letter-spacing:-.01em;}
  .hero--plain .sub{margin:24px auto 0;color:var(--ink-d);}
  .hero__cta{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:32px;}
  .hero__note{margin-top:18px;font-size:12.5px;color:rgba(26,26,28,.46);letter-spacing:.01em;}
  .hero--plain .hero__note{color:var(--ink-3);}

  /* 스크린샷 — aside 브라우저 프레임과 같은 폭(1320)·여백(60)·음수 마진(-128) */
  .shotwrap{position:relative;z-index:1;width:100%;margin-bottom:-128px;}
  .hero__shot{max-width:1320px;margin:0 auto;padding:0 60px;}
  .hero__shot img{width:100%;height:auto;border-radius:12px;
    box-shadow:0 20px 25px -5px rgba(0,0,0,.1),0 8px 10px -6px rgba(0,0,0,.1);}
  .after-hero{padding-top:96px;}

  /* 서브페이지 히어로 — aside 는 pt-16 pb-8 에 흰 배경 */
  .hero--plain{padding:64px var(--pad) 32px;}

  /* 덱 eyebrow 와 같은 문법 — 오렌지 보더 / 대문자 / 넓은 자간 */
  .pill{display:inline-flex;align-items:center;gap:8px;height:31px;padding:0 15px;
    border:1px solid var(--accent);border-radius:3px;font-size:12px;font-weight:500;
    color:var(--accent);background:transparent;letter-spacing:.14em;text-transform:uppercase;
    margin-bottom:26px;}
  .pill i{width:5px;height:5px;border-radius:50%;background:var(--accent);}

  @media (min-width:768px){
    .hero h1{font-size:50px;}
    .hero .sub{font-size:17px;margin-top:26px;}
  }
  @media (min-width:1200px){
    .hero h1{font-size:68px;}          /* nextsaas 제목 5.2→6.8rem */
    .hero .sub{font-size:18px;margin-top:30px;}
  }
  .rise{animation:rise .8s cubic-bezier(.22,.7,.3,1) both;}
  .r2{animation-delay:.07s;} .r3{animation-delay:.14s;} .r4{animation-delay:.22s;}
  @keyframes rise{from{opacity:0;transform:translateY(18px);}to{opacity:1;transform:none;}}

  /* ── 섹션 공통 ─────────────────────────────────────────── */
  .head{max-width:var(--prose);margin:0 auto;text-align:center;}

  .head h2{font-size:32px;font-weight:400;line-height:1.1;margin-top:20px;}
  @media (min-width:768px){ .head h2{font-size:46px;} }
  @media (min-width:1200px){ .head h2{font-size:60px;} }
  /* 덱 헤드라인 - 첫 줄은 보통, 둘째 줄이 검정 볼드. 오렌지는 눈썹/수치에만 쓴다 */
  .head h2 b{font-weight:700;color:var(--ink-t);letter-spacing:-.028em;}
  .head p:not(.kicker){margin-top:22px;font-size:16px;line-height:1.6;color:var(--ink-d);
    font-weight:400;letter-spacing:-.01em;}
  @media (min-width:1200px){ .head p:not(.kicker){margin-top:26px;font-size:18px;} }
  /* 덱은 헤드라인 바로 아래 오렌지 볼드 한 줄로 핵심을 박는다.
     .head p:not(.kicker) 가 (0,2,1) 이라 p.punch 로 특이도를 맞추고 뒤에 둔다. */
  .head p.punch{color:var(--accent);font-weight:700;}
  .head--left{text-align:left;max-width:920px;}
  .frame--panel{background:var(--panel);}
  .lede{max-width:60ch;margin:36px auto 0;font-size:17px;line-height:1.8;color:var(--ink-d);
    font-weight:400;text-align:center;}
  .lede b{color:var(--ink-t);font-weight:700;}

  /* 라벨 좌 / 본문 우 */
  .duo{display:grid;grid-template-columns:200px 1fr;gap:56px;max-width:1000px;margin:0 auto;}
  .duo__b{font-size:17px;line-height:1.8;color:var(--ink-d);font-weight:400;}
  .duo__b b{color:var(--ink-t);font-weight:700;}
  .duo__b p + p{margin-top:18px;}

  /* ── 아이콘 월 ─────────────────────────────────────────── */
  .wall{position:relative;height:330px;margin-top:34px;overflow:hidden;
    -webkit-mask-image:linear-gradient(#000 0%,#000 55%,transparent 100%);
    mask-image:linear-gradient(#000 0%,#000 55%,transparent 100%);}
  .wall__p{position:absolute;inset:0;display:flex;justify-content:center;perspective:1250px;}
  .wall__g{display:grid;grid-template-columns:repeat(9,86px);gap:16px;transform-origin:bottom center;
    animation:drift 42s linear infinite;}
  @keyframes drift{
    from{transform:rotateX(47deg) scale(1.14) translateY(0);}
    to{transform:rotateX(47deg) scale(1.14) translateY(-204px);}
  }
  .wt{width:86px;height:86px;border-radius:19px;background:#fff;border:1px solid var(--hair);
    box-shadow:0 2px 10px -5px rgba(10,10,10,.22);display:grid;place-items:center;padding:13px;}
  .wt img{width:100%;height:100%;object-fit:contain;}

  /* ── 카드 3열 — 원본 비율 유지(잘리거나 찌그러지지 않게) ──── */
  .tri{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:52px;align-items:start;}
  .tri__c img{width:100%;height:auto;border-radius:12px;border:1px solid var(--hair);
    background:var(--panel);}
  .tri__c p{margin-top:15px;font-size:14px;line-height:1.75;color:var(--ink-2);font-weight:400;}
  .tri__c b{color:var(--ink);font-weight:500;}

  /* ── 활용 사례 그라데이션 카드 ──────────────────────────── */
  /* 덱 카드 - 흰 바탕 / radius 12 / 상단 오렌지 엣지 / 작은 오렌지 라벨 + 검정 볼드 제목.
     강조할 한 장만 오렌지로 채운다(덱 1/9/16장의 문법). */
  .cases{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:52px;}
  .case{background:#fff;border-radius:12px;padding:26px 24px 24px;
    box-shadow:0 1px 2px rgba(26,26,28,.05),0 10px 24px -18px rgba(26,26,28,.35);
    border-top:3px solid var(--accent);}
  .case__g{display:flex;flex-direction:column;gap:5px;}
  .case__g span{font-size:11.5px;font-weight:500;letter-spacing:.13em;text-transform:uppercase;
    color:var(--accent);line-height:1;}
  .case__g span:last-child{font-size:21px;font-weight:700;letter-spacing:-.025em;line-height:1.2;
    color:var(--ink-t);text-transform:none;margin-top:3px;}
  .case p{margin-top:13px;font-size:14px;line-height:1.75;color:var(--ink-2);font-weight:400;}
  .case p b{color:var(--ink-t);font-weight:700;}
  /* 카드 첫머리 라벨(예: '수주 제안서')만 줄을 차지한다. 문장 중간 강조는 인라인. */
  .case p > b:first-child{display:block;color:var(--ink);font-weight:500;margin-bottom:2px;}
  /* 강조 카드 - 흰 글자 대비 5.18:1 이 나오는 딥 오렌지를 바탕으로 */
  .case--hi{background:linear-gradient(140deg,var(--accent-b) 0%,var(--accent) 58%);
    border-top-color:rgba(255,255,255,.55);}
  .case--hi .case__g span{color:rgba(255,255,255,.88);}
  .case--hi .case__g span:last-child,.case--hi b,.case--hi p b{color:#fff;}
  .case--hi p{color:rgba(255,255,255,.92);}

  /* ── 효과 카드 — 덱 14장의 기존/현재 막대 비교 ─────────── */
  .effect{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin-top:52px;}
  .effect__c{background:#fff;border-radius:12px;padding:28px 26px 24px;
    border-top:3px solid var(--accent);
    box-shadow:0 1px 2px rgba(26,26,28,.05),0 10px 24px -18px rgba(26,26,28,.35);}
  .effect__l{font-size:11.5px;font-weight:500;letter-spacing:.13em;text-transform:uppercase;
    color:var(--accent);line-height:1;}
  .effect__v{margin-top:11px;font-size:27px;font-weight:400;letter-spacing:-.03em;
    color:var(--ink-3);line-height:1.2;}
  .effect__v b{font-weight:700;color:var(--ink-t);}
  .effect .bench{margin-top:19px;gap:9px;max-width:none;}
  .effect .brow{grid-template-columns:78px 1fr 112px;gap:12px;}
  .effect__n{margin-top:15px;font-size:13px;line-height:1.7;color:var(--ink-2);font-weight:400;}
  .effect__n b{color:var(--ink-t);font-weight:700;}

  /* ── 벤치마크 바 ───────────────────────────────────────── */
  .bench{margin-top:44px;display:grid;gap:14px;max-width:880px;}
  .brow{display:grid;grid-template-columns:210px 1fr 62px;gap:20px;align-items:center;}
  .brow__n{font-size:14px;}
  .brow__n span{display:block;font-size:11.5px;color:var(--ink-3);}
  .brow__t{height:24px;border-radius:6px;background:#EDEFF1;overflow:hidden;}
  .brow__t i{display:block;height:100%;border-radius:6px;background:#D5D8DC;}
  .brow--hi .brow__t i{background:linear-gradient(90deg,var(--accent-b),var(--accent));}
  .brow__v{font-size:14px;text-align:right;font-variant-numeric:tabular-nums;color:var(--ink-2);}
  .brow--hi .brow__v{color:var(--ink);}

  /* ── 검색 교정 박스 ────────────────────────────────────── */
  .qb{border:1px solid var(--hair);border-radius:12px;overflow:hidden;background:#fff;max-width:880px;
    margin:44px auto 0;}
  .qb__h{padding:13px 20px;border-bottom:1px solid var(--hair);font-size:11.5px;color:var(--ink-3);
    letter-spacing:.07em;text-transform:uppercase;}
  .qr{padding:16px 20px;border-bottom:1px solid var(--hair);display:flex;align-items:center;gap:14px;
    flex-wrap:wrap;}
  .qr:last-child{border-bottom:0;}
  .qi{display:inline-flex;align-items:center;height:33px;padding:0 15px;border-radius:999px;
    background:var(--panel);font-size:14px;}
  .qo{font-size:14px;color:var(--ink-2);font-weight:400;}
  .qo b{color:var(--ink);font-weight:500;}
  .qo em{font-style:normal;color:var(--accent);font-variant-numeric:tabular-nums;}

  /* ── 통계 스트립 ───────────────────────────────────────── */
  .stats{display:grid;grid-template-columns:repeat(6,1fr);border-top:1px solid var(--hair);}
  .stats > div{padding:26px 10px;text-align:center;border-right:1px solid var(--hair);}
  .stats > div:last-child{border-right:0;}
  .stats b{display:block;font-size:25px;font-weight:500;letter-spacing:-.035em;
    font-variant-numeric:tabular-nums;}
  .stats span{display:block;font-size:12.5px;color:var(--ink-2);margin-top:3px;}

  /* ── 좌우 분할 ─────────────────────────────────────────── */
  .split{display:grid;grid-template-columns:1fr 1.15fr;gap:72px;align-items:center;}
  .split--f .split__v{order:-1;}
  .split h2{font-size:clamp(25px,3vw,36px);line-height:1.2;margin-top:14px;}
  .split h2 b{font-weight:700;color:var(--ink-t);letter-spacing:-.028em;}
  .split > div > p{margin-top:16px;font-size:16px;line-height:1.8;color:var(--ink-2);font-weight:400;
    max-width:42ch;}
  .split__v img{width:100%;border-radius:12px;border:1px solid var(--hair);
    box-shadow:0 2px 8px rgba(10,10,10,.05),0 34px 70px -46px rgba(10,10,10,.4);}
  .list{margin-top:26px;display:grid;gap:13px;}
  .list li{display:flex;gap:11px;font-size:15px;line-height:1.75;color:var(--ink-2);font-weight:400;}
  .list b{color:var(--ink);font-weight:500;}
  .list i{flex-shrink:0;width:5px;height:5px;border-radius:50%;background:var(--ink);opacity:.28;
    margin-top:11px;}

  /* ── 비교표 ────────────────────────────────────────────── */
  .cmp{margin-top:48px;max-width:1000px;margin-inline:auto;}
  .cmp table{border-collapse:collapse;width:100%;font-size:14.5px;}
  .cmp th{font-weight:400;font-size:12.5px;color:var(--ink-2);padding:0 0 16px;text-align:center;}
  .cmp th:first-child{text-align:left;}
  .cmp th b{display:block;color:var(--ink);font-size:14px;font-weight:500;}
  .cmp td{padding:16px 0;border-top:1px solid var(--hair);text-align:center;width:130px;}
  .cmp td:first-child{text-align:left;width:auto;color:var(--ink-2);font-weight:400;}
  .ck{color:#1F9254;} .cx{color:#C8CBD0;}

  /* ── 요금제 ────────────────────────────────────────────── */
  .toggle{display:inline-flex;padding:4px;border-radius:999px;background:var(--panel);margin-top:28px;gap:2px;}
  .toggle button{appearance:none;border:0;background:none;font:inherit;cursor:pointer;
    padding:8px 19px;border-radius:999px;font-size:13.5px;color:var(--ink-2);
    transition:background .16s,color .16s,box-shadow .16s;}
  .toggle button:hover{color:var(--ink);}
  .toggle button.on{background:#fff;color:var(--ink);font-weight:500;
    box-shadow:0 1px 3px rgba(10,10,10,.12);}
  .pl__p b{transition:opacity .14s;}
  .pl__p.is-swap b,.pl__p.is-swap span{opacity:.25;}
  .plans{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:56px;align-items:stretch;}
  /* nextsaas 카드 — 흰 배경 · radius 20 · padding 32 · 보더와 그림자 없음 */
  .pl{background:#fff;border-radius:20px;padding:32px;display:flex;flex-direction:column;}
  .pl__n{font-size:15.5px;font-weight:500;}
  .pl__n span{color:var(--ink-3);font-weight:400;}
  .pl__p{display:flex;align-items:baseline;gap:5px;margin-top:20px;}
  .pl__p b{font-size:44px;font-weight:500;letter-spacing:-.045em;font-variant-numeric:tabular-nums;
    line-height:1.1;}
  .pl__p span{font-size:13px;color:var(--ink-3);}
  .pl ul{margin-top:26px;margin-bottom:34px;display:grid;gap:13px;font-size:14.5px;color:var(--ink-2);font-weight:400;}
  .pl li{display:flex;gap:10px;line-height:1.6;}
  .pl li b{color:var(--ink);font-weight:500;}
  .pl li svg{flex-shrink:0;margin-top:5px;color:#1F9254;}
  .pl .btn{width:100%;margin-top:auto;}   /* 카드 높이가 달라도 버튼은 바닥에 정렬 */
  .ent{border:1px solid var(--hair);border-radius:20px;padding:40px;margin-top:24px;}
  .ent h3{font-size:24px;font-weight:500;margin-top:10px;}
  .ent > p{margin-top:12px;font-size:15.5px;color:var(--ink-2);font-weight:400;max-width:56ch;line-height:1.8;}
  .ent ul{margin-top:32px;display:grid;gap:12px;font-size:14.5px;color:var(--ink-2);font-weight:400;
    max-width:74ch;}
  .ent li{display:flex;gap:10px;line-height:1.6;}
  .ent li svg{flex-shrink:0;margin-top:5px;color:#1F9254;}

  /* ── FAQ ──────────────────────────────────────────────── */
  .faq{max-width:760px;margin:44px auto 0;border-top:1px solid var(--hair);}
  .fi{padding:26px 0;border-bottom:1px solid var(--hair);}
  .fq{font-size:16.5px;font-weight:500;letter-spacing:-.015em;}
  .fa{margin-top:10px;font-size:15px;line-height:1.9;color:var(--ink-2);font-weight:400;}

  /* ── CTA 밴드 ──────────────────────────────────────────── */
  /* nextsaas 다크 패널 — #1A1A1C · radius 32 · padding 72/42 + 모서리 글로우 */
  .cta{position:relative;overflow:hidden;border-radius:32px;padding:72px 42px;text-align:center;
    background:var(--dark);color:#FCFCFC;}
  .cta::before{content:"";position:absolute;right:-12%;top:-42%;width:62%;height:150%;
    pointer-events:none;
    background:
      radial-gradient(42% 42% at 62% 44%, rgba(224,112,31,.85) 0%, rgba(224,112,31,0) 68%),
      radial-gradient(38% 38% at 34% 62%, rgba(150,120,255,.62) 0%, rgba(150,120,255,0) 68%),
      radial-gradient(34% 34% at 76% 70%, rgba(96,205,225,.48) 0%, rgba(96,205,225,0) 68%);
    filter:blur(18px);}
  .cta > *{position:relative;z-index:1;}
  .cta h2{font-size:32px;font-weight:500;line-height:1.12;color:#FCFCFC;}
  @media (min-width:768px){ .cta h2{font-size:46px;} }
  @media (min-width:1200px){ .cta h2{font-size:56px;} }
  .cta .hero__cta{margin-top:34px;}
  .cta .btn--d{background:#FCFCFC;color:var(--dark);}
  .cta .btn--d:hover{background:#E9E9EA;}
  .cta .btn--s{background:rgba(252,252,252,.1);color:#FCFCFC;border-color:rgba(252,252,252,.22);}
  .cta .btn--s:hover{background:rgba(252,252,252,.18);border-color:rgba(252,252,252,.34);}

  /* ── 푸터 ─────────────────────────────────────────────── */
  .foot{border-top:1px solid var(--hair);}
  .foot__in{max-width:var(--page);margin:0 auto;padding:64px var(--pad) 0;
    border-left:1px solid var(--hair);border-right:1px solid var(--hair);}
  .fgrid{display:grid;grid-template-columns:repeat(5,1fr);gap:28px;}
  .fcol h4{font-size:11.5px;color:var(--ink-3);font-weight:400;margin:0 0 14px;letter-spacing:.08em;
    text-transform:uppercase;}
  .fcol a{display:block;font-size:14px;text-decoration:none;color:var(--ink);margin-bottom:11px;}
  .fcol a:hover{color:var(--accent);}
  .fbar{margin-top:64px;padding:22px 0 52px;border-top:1px solid var(--hair);display:flex;gap:16px;
    flex-wrap:wrap;align-items:center;}
  .fbar p{font-size:12.5px;color:var(--ink-3);}
  .fbar .brand{margin-right:auto;}


  /* ── 맨 위로 ───────────────────────────────────────────── */
  .totop{position:fixed;right:24px;bottom:24px;z-index:80;width:46px;height:46px;
    display:grid;place-items:center;border-radius:50%;border:1px solid var(--line);
    background:rgba(255,255,255,.92);backdrop-filter:blur(10px);cursor:pointer;
    color:var(--ink);box-shadow:0 6px 20px -6px rgba(10,10,10,.28);
    opacity:0;visibility:hidden;transform:translateY(10px);
    transition:opacity .22s,transform .22s,visibility .22s,border-color .16s;}
  .totop.is-on{opacity:1;visibility:visible;transform:none;}
  .totop:hover{border-color:#B9BCC1;}
  .totop svg{display:block;}

  /* ── 모바일 메뉴 ───────────────────────────────────────── */
  .burger{display:none;width:36px;height:36px;border:1px solid var(--line);border-radius:999px;
    background:#fff;cursor:pointer;padding:0;place-items:center;}
  .skycard .burger{background:rgba(255,255,255,.7);border-color:rgba(9,11,12,.18);}
  .burger i{display:block;width:15px;height:1.5px;background:var(--ink);border-radius:2px;
    position:relative;transition:background .16s;}
  .burger i::before,.burger i::after{content:"";position:absolute;left:0;width:15px;height:1.5px;
    background:var(--ink);border-radius:2px;transition:transform .2s;}
  .burger i::before{top:-5px;} .burger i::after{top:5px;}
  .nav.is-open .burger i{background:transparent;}
  .nav.is-open .burger i::before{transform:translateY(5px) rotate(45deg);}
  .nav.is-open .burger i::after{transform:translateY(-5px) rotate(-45deg);}

  /* ── FAQ 아코디언 ──────────────────────────────────────── */
  .fq-btn{display:flex;width:100%;align-items:flex-start;justify-content:space-between;gap:16px;
    appearance:none;border:0;background:none;font:inherit;text-align:left;cursor:pointer;padding:0;
    color:inherit;}
  .fq-btn .fq{flex:1;}
  .fq-mark{flex:none;width:22px;height:22px;margin-top:2px;position:relative;}
  .fq-mark::before,.fq-mark::after{content:"";position:absolute;left:50%;top:50%;background:var(--ink-3);
    border-radius:2px;transform:translate(-50%,-50%);transition:transform .22s,background .16s;}
  .fq-mark::before{width:12px;height:1.5px;}
  .fq-mark::after{width:1.5px;height:12px;}
  .fi.is-open .fq-mark::after{transform:translate(-50%,-50%) scaleY(0);}
  .fi.is-open .fq-mark::before{background:var(--brand);}
  .fq-btn:hover .fq-mark::before,.fq-btn:hover .fq-mark::after{background:var(--ink);}
  .fa-wrap{display:grid;grid-template-rows:0fr;transition:grid-template-rows .26s ease;}
  .fi.is-open .fa-wrap{grid-template-rows:1fr;}
  .fa-wrap > div{overflow:hidden;}

  /* ── 앵커 이동이 고정 내비에 가리지 않게 ───────────────── */
  [id]{scroll-margin-top:80px;}

  @media (max-width:1000px){
    .burger{display:grid;}
    .nav.is-open .nav__l{display:flex;position:absolute;left:0;right:0;top:56px;transform:none;
      flex-direction:column;gap:0;background:#fff;border-top:1px solid var(--hair);
      box-shadow:0 20px 34px -22px rgba(10,10,10,.45);padding:6px 16px 14px;}
    .nav.is-open .nav__l a{padding:13px 2px;font-size:16px;border-bottom:1px solid var(--hair);}
    .nav.is-open .nav__l a:last-child{border-bottom:0;}
    .totop{right:16px;bottom:16px;width:42px;height:42px;}
  }
  @media (prefers-reduced-motion: reduce){
    html{scroll-behavior:auto;}
    .fa-wrap{transition:none;}
  }


  @media (max-width:560px){
    .nav__r .btn--s{display:none;}   /* 좁은 화면에선 Docs 는 메뉴 안에 있다 */
    .brand__t{font-size:16px;}
  }
  @media (max-width:1279px){ :root{--pad:56px;} }
  @media (max-width:1000px){
  :root{--pad:32px;}
    .frame{padding-top:64px;padding-bottom:64px;}
    .nav__l{display:none;}
    .hero{padding:48px 16px;}
    .hero .sub{margin-top:24px;}
    .hero--plain{padding:48px var(--pad) 28px;}
    .skywrap{padding:8px 8px 0;}
    .skycard{border-radius:20px;}
    .hero__shot{padding:0 20px;}
    .shotwrap{margin-bottom:-56px;}
    .after-hero{padding-top:56px;}
    .duo{grid-template-columns:1fr;gap:18px;}
    .tri,.cases,.effect{grid-template-columns:1fr;gap:26px;}
    .split{grid-template-columns:1fr;gap:34px;} .split--f .split__v{order:0;}
    .plans{grid-template-columns:1fr;gap:52px;}
    .stats{grid-template-columns:repeat(3,1fr);}
    .stats > div:nth-child(3n){border-right:0;}
    .stats > div:nth-child(-n+3){border-bottom:1px solid var(--hair);}
    .brow{grid-template-columns:1fr;gap:7px;} .brow__v{text-align:left;}
    .fgrid{grid-template-columns:repeat(2,1fr);gap:32px;}
    .wall{height:230px;}
    .ent{padding:30px;}
    .cta{padding:80px 24px 86px;}
    :root{--pad:24px;}
    .cmp td{width:74px;}
  }
  @media (prefers-reduced-motion: reduce){
    *{animation:none !important;transition:none !important;}
    .wall__g{transform:rotateX(47deg) scale(1.14);}
  }
"""

LOGO = ('<span class="brand__m" aria-hidden="true"><svg width="12" height="12" viewBox="0 0 14 14" '
        'fill="none"><path d="M7 2v10M2 7h10" stroke="#fff" stroke-width="2.1" stroke-linecap="round"/>'
        '</svg></span><span class="brand__t">powerPlus</span>')

TOTOP = '<button class="totop" type="button" aria-label="맨 위로"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M8 13V3M8 3L3.5 7.5M8 3l4.5 4.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>'

BURGER = '<button class="burger" type="button" aria-label="메뉴 열기" aria-expanded="false"><i aria-hidden="true"></i></button>'

SITE_JS = '\n<script>\n(function(){\n  "use strict";\n  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;\n\n  /* 1. 맨 위로 */\n  var top = document.querySelector(".totop");\n  if (top) {\n    var toggleTop = function(){ top.classList.toggle("is-on", window.scrollY > 420); };\n    toggleTop();\n    window.addEventListener("scroll", toggleTop, {passive:true});\n    top.addEventListener("click", function(){\n      window.scrollTo({top:0, behavior: reduce ? "auto" : "smooth"});\n    });\n  }\n\n  /* 2. 모바일 메뉴 */\n  var nav = document.querySelector(".nav");\n  var burger = nav && nav.querySelector(".burger");\n  if (nav && burger) {\n    var close = function(){ nav.classList.remove("is-open"); burger.setAttribute("aria-expanded","false"); };\n    burger.addEventListener("click", function(){\n      var open = !nav.classList.contains("is-open");\n      nav.classList.toggle("is-open", open);\n      burger.setAttribute("aria-expanded", open ? "true" : "false");\n    });\n    nav.querySelectorAll(".nav__l a").forEach(function(a){ a.addEventListener("click", close); });\n    document.addEventListener("keydown", function(e){ if (e.key === "Escape") close(); });\n    document.addEventListener("click", function(e){ if (!nav.contains(e.target)) close(); });\n    window.addEventListener("resize", function(){ if (window.innerWidth > 1000) close(); });\n  }\n\n  /* 3. FAQ 아코디언 — 스크립트가 없으면 그냥 다 펼쳐진 문서로 읽힌다 */\n  document.querySelectorAll(".faq .fi").forEach(function(item, i){\n    var q = item.querySelector(".fq"), a = item.querySelector(".fa");\n    if (!q || !a) return;\n    var btn = document.createElement("button");\n    btn.type = "button";\n    btn.className = "fq-btn";\n    btn.setAttribute("aria-expanded", "false");\n    q.parentNode.insertBefore(btn, q);\n    btn.appendChild(q);\n    var mark = document.createElement("span");\n    mark.className = "fq-mark";\n    mark.setAttribute("aria-hidden", "true");\n    btn.appendChild(mark);\n\n    var wrap = document.createElement("div");\n    wrap.className = "fa-wrap";\n    var innerId = "fa-" + (i + 1);\n    var inner = document.createElement("div");\n    a.parentNode.insertBefore(wrap, a);\n    inner.appendChild(a);\n    wrap.appendChild(inner);\n    wrap.id = innerId;\n    btn.setAttribute("aria-controls", innerId);\n\n    btn.addEventListener("click", function(){\n      var open = !item.classList.contains("is-open");\n      item.classList.toggle("is-open", open);\n      btn.setAttribute("aria-expanded", open ? "true" : "false");\n    });\n  });\n\n  /* 4. 같은 페이지 앵커 — 부드럽게, 그리고 주소창에도 남게 */\n  var here = location.pathname.split("/").pop() || "index.html";\n  document.querySelectorAll(\'a[href*="#"]\').forEach(function(a){\n    a.addEventListener("click", function(e){\n      var href = a.getAttribute("href") || "";\n      if (/^(https?:|mailto:|tel:)/.test(href)) return;\n      var parts = href.split("#");\n      if (parts[0] && parts[0] !== here) return;   /* 다른 페이지면 평소대로 이동 */\n      var id = parts[1];\n      var el = id && document.getElementById(id);\n      if (!el) return;\n      e.preventDefault();\n      el.scrollIntoView({behavior: reduce ? "auto" : "smooth", block:"start"});\n      history.replaceState(null, "", "#" + id);\n    });\n  });\n})();\n</script>\n'

NAVLINKS = [('features', '기능'), ('usecases', '활용 사례'), ('pricing', '요금제'), ('docs', '문서')]

MAIL = 'mailto:solideosai15@solideos.com?subject=powerPlus%20%EB%AC%B8%EC%9D%98'


def nav(active):
    links = ''.join('<a href="{{%s}}"%s>%s</a>' % (k.upper(), ' class="on"' if k == active else '', t)
                    for k, t in NAVLINKS)
    return ('<header class="nav"><div class="nav__in">'
            '<a class="brand" href="{{HOME}}">%s</a>'
            '<nav class="nav__l">%s</nav>'
            '<div class="nav__r">'
            '<a class="btn btn--sm btn--s" href="{{DOCS}}">Docs</a>'
            '<a class="btn btn--sm btn--d" href="%s">무료로 시작</a>'
            '%s'
            '</div></div></header>' % (LOGO, links, MAIL, BURGER))


CTA = ('<section class="band"><div class="frame frame--tight"><div class="cta">'
       '<h2>흩어진 자료를 회사의 자산으로.<br>오늘 시작하세요.</h2>'
       '<div class="hero__cta">'
       '<a class="btn btn--d" href="%s">무료로 시작</a>'
       '<a class="btn btn--s" href="{{DOCS}}">Read the docs</a>'
       '</div></div></div></section>' % MAIL)

FOOTER = ('<footer class="foot"><div class="foot__in"><div class="fgrid">'
          '<div class="fcol"><h4>Product</h4>'
          '<a href="{{FEATURES}}#library">자산 라이브러리</a>'
          '<a href="{{FEATURES}}#search">한국어 검색</a>'
          '<a href="{{FEATURES}}#decks">장표 삽입</a></div>'
          '<div class="fcol"><h4>Use cases</h4>'
          '<a href="{{USECASES}}">제안서</a>'
          '<a href="{{USECASES}}">사내 보고</a>'
          '<a href="{{USECASES}}">교육 자료</a></div>'
          '<div class="fcol"><h4>Resources</h4>'
          '<a href="{{DOCS}}#install">설치 안내</a>'
          '<a href="{{DOCS}}#changelog">릴리스 노트</a>'
          '<a href="{{DOCS}}#faq">문제 해결</a></div>'
          '<div class="fcol"><h4>Company</h4>'
          '<a href="{{HOME}}">powerPlus 소개</a>'
          '<a href="%s">문의</a></div>'
          '<div class="fcol"><h4>Pricing</h4>'
          '<a href="{{PRICING}}">요금제</a>'
          '<a href="{{PRICING}}#selfhost">구축형</a></div>'
          '</div><div class="fbar"><a class="brand" href="{{HOME}}">%s</a>'
          '<p>화면과 수치는 운영 중인 라이브러리의 실제 데이터입니다. · Updated 2026-09-20</p>'
          '</div></div></footer>' % (MAIL, LOGO))


def page(title, desc, active, body, sky=False):
    return ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="description" content="%s">\n'
            ''
            '<style>html{color-scheme:light}body{margin:0}img{max-width:100%%}'
            '[hidden]{display:none!important}</style>\n'
            '<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n%s\n<main>\n%s\n%s\n</main>\n%s\n%s%s'

            '</body>\n</html>\n' % (desc, title, CSS,
                                      '' if sky else nav(active), body, CTA, FOOTER,
                                      TOTOP, SITE_JS))


# ══════════════════════════════════════════════════════════ HOME
HOME = """
<div class="skywrap">
  <div class="skycard">
    __NAV__
    <header class="hero">
      <span class="pill rise"><i aria-hidden="true"></i>PowerPoint Add-in</span>
      <h1 class="rise r2">한 번 쓰고 버려지던 자료가,<br><b>회사의 자산으로 쌓입니다.</b></h1>
      <p class="sub rise r2">개인 PC에 흩어져 사라지던 아이콘·사진·장표를 전사가 함께 쓰는 라이브러리에 모읍니다. 같은 곳에서 꺼내 쓰니 누가 맡아도 제안서의 톤이 흔들리지 않습니다.</p>
      <div class="hero__cta rise r3">
        <a class="btn btn--lg btn--d" href="__MAIL__">무료로 시작</a>
        <a class="btn btn--lg btn--s" href="{{FEATURES}}">기능 살펴보기</a>
      </div>
      <p class="hero__note rise r3">Office 2019 · 2021 · Microsoft 365 — Windows &amp; macOS</p>
    </header>
    <div class="shotwrap rise r4">
      <div class="hero__shot">
        <img src="shots/shot-deck.jpg" width="1400" height="761"
          alt="파워포인트 오른쪽에 powerPlus 자산 라이브러리 작업창이 열려 아이콘이 격자로 나열된 실제 화면">
      </div>
    </div>
  </div>
</div>

<section class="band band--plain"><div class="frame after-hero">
  <div class="duo">
    <p class="kicker">Why powerPlus</p>
    <div class="duo__b">
      <p><b>제안서 하나가 끝나면 그때 모은 자료도 같이 끝납니다.</b> 골라 둔 아이콘과 배경 사진, 공들여 만든 표지는 담당자 PC 폴더에 남고, 다음 제안서를 맡은 사람은 같은 자료를 처음부터 다시 찾습니다.</p>
      <p>여럿이 나눠 만들다 보면 각자 다른 곳에서 자료를 가져옵니다. <b>같은 회사가 낸 제안서인데 장마다 톤이 다릅니다.</b> 출처도 권한도 제각각이라 나중에 다시 쓰기도 어렵습니다.</p>
      <p><b>제일 오래 걸리는 건 글쓰기가 아니라 자료 찾기입니다.</b> 아이콘 하나 찾자고 지난 제안서 폴더를 뒤지고, 없으면 인터넷에서 새로 받습니다. 그렇게 받은 자료는 또 그 사람 PC 에만 남습니다.</p>
      <p>powerPlus는 그 자료를 버리지 않고 <b>전사가 함께 쓰는 라이브러리</b>에 쌓습니다. 그리고 그 검색창을 파워포인트 안으로 옮겨, 다음 사람이 같은 자산을 꺼내 쓰게 만듭니다.</p>
    </div>
  </div>
</div></section>

<section class="band"><div class="frame">
  <div class="head">
    <p class="kicker">What we tried</p>
    <h2>모아 두는 것과<br><b>꺼내 쓰는 것은 다릅니다.</b></h2>
    <p class="punch">아무리 잘 정리해 두어도, 가져다 쓰기 불편하면 쓰지 않습니다.</p>
    <p>공유 폴더도 만들어 봤고, 장표를 한 파일에 모아도 봤습니다. 둘 다 오래가지 않았습니다. 찾으려면 결국 폴더를 열고 눈으로 훑어야 했기 때문입니다.</p>
  </div>
  <div class="cases">
    <div class="case"><div class="case__g"><span>Attempt 01</span><span>공유 폴더</span></div>
      <p>폴더를 열고 눈으로 훑어야 찾습니다. 이름을 모르면 있는 줄도 모르고, 결국 각자 PC 에 사본을 따로 둡니다.</p></div>
    <div class="case"><div class="case__g"><span>Attempt 02</span><span>정리용 파워포인트</span></div>
      <p>지난 장표에서 콘텐츠만 모아 <b>540장</b>짜리 한 파일로 만들었습니다. 그래도 쓰려면 그 파일을 열고 장을 하나하나 넘겨 봐야 했습니다.</p></div>
    <div class="case case--hi"><div class="case__g"><span>Now</span><span>powerPlus</span></div>
      <p>파워포인트를 닫지 않고, 작업창 안에서 한국어로 검색해 지금 슬라이드에 바로 넣습니다. 찾는 자리와 쓰는 자리가 같습니다.</p></div>
  </div>
</div></section>

<section class="band"><div class="frame frame--flush frame--panel">
  <div class="inner">
    <div class="head">
      <p class="kicker">Accumulate</p>
      <h2>버려질 자료가<br><b>3,734개의 자산이</b> 됐습니다.</h2>
    </div>
  </div>
  <div class="wall" aria-hidden="true"><div class="wall__p"><div class="wall__g">__WALL__</div></div></div>
  <div class="stats">
    <div><b>1,586</b><span>아이콘</span></div>
    <div><b>731</b><span>장표</span></div>
    <div><b>539</b><span>로고</span></div>
    <div><b>378</b><span>일러스트</span></div>
    <div><b>354</b><span>사진</span></div>
    <div><b>146</b><span>다이어그램</span></div>
  </div>
  <div class="inner">
    <p class="lede">나간 제안서를 <b>표지·목차·간지·본문 낱장</b>으로 잘라 등록하고, 아이콘과 사진에는 국문 25개·영문 25개 키워드를 붙여 담습니다. 개인 폴더에서 끝났을 자료가 다음 제안서에서 다시 쓰입니다.</p>
  </div>
</div></section>

<section class="band"><div class="frame">
  <div class="head">
    <p class="kicker">One library</p>
    <h2>누가 맡아도<br><b>같은 톤으로 나옵니다.</b></h2>
    <p>여럿이 나눠 만들어도 자산을 한곳에서 꺼내 쓰면 제안서의 결이 흔들리지 않습니다. 장마다 다른 아이콘, 다른 색을 쓰던 일이 없어집니다.</p>
  </div>
  <div class="tri">
    <div class="tri__c">
      <img src="shots/shot-set.jpg" alt="같은 스타일 세트를 열어 함께 등록된 장표가 격자로 보이는 화면" loading="lazy">
      <p><b>Style sets</b> 색감·채도·밝기를 실측해 같은 결의 자산만 묶었습니다. 한 장 안에 여러 개를 써도 톤이 어긋나지 않습니다.</p>
    </div>
    <div class="tri__c">
      <img src="shots/shot-logo-full.jpg" alt="로고 카테고리를 선택해 기관 성격별 로고가 나열된 작업창" loading="lazy">
      <p><b>Logos</b> 정부 부처·지자체·공단으로 나눠 둡니다. 담당자마다 다른 로고 파일을 쓰던 일이 없어집니다.</p>
    </div>
    <div class="tri__c">
      <img src="shots/shot-illust.jpg" alt="일러스트 카테고리를 선택해 인물 일러스트가 나열된 작업창" loading="lazy">
      <p><b>Illustrations</b> 회의·발표·분석처럼 쓰이는 장면으로 나눠 뒀습니다. 같은 화풍 안에서 고르게 됩니다.</p>
    </div>
  </div>
</div></section>

<section class="band"><div class="frame">
  <div class="head">
    <p class="kicker">Findable</p>
    <h2>쌓아 두기만 하면<br><b>없는 것과 같습니다.</b></h2>
    <p>사람은 자산에 붙은 이름을 모르고 검색합니다. powerPlus는 자산을 늘리는 대신 검색어 쪽을 고쳐, 쌓아 둔 자산이 실제로 쓰이게 만듭니다.</p>
  </div>
  <div class="qb">
    <div class="qb__h">Query correction — live behavior</div>
    <div class="qr"><span class="qi">코그</span><span class="qo"><b>‘코드’</b>로 고쳐서 찾았어요 · <em>38개</em></span></div>
    <div class="qr"><span class="qi">디비</span><span class="qo"><b>데이터베이스</b>와 같은 결과 · <em>124개</em></span></div>
    <div class="qr"><span class="qi">사람들</span><span class="qo">어간까지 넓혀서 · <em>243개</em></span></div>
    <div class="qr"><span class="qi">성장 전략</span><span class="qo">상승·로드맵·목표까지 · <em>86개</em></span></div>
  </div>
</div></section>

<section class="band"><div class="frame">
  <div class="head">
    <p class="kicker">Effect</p>
    <h2>찾는 시간이 줄면<br><b>만드는 장수가 늘어납니다.</b></h2>
    <p class="punch">아래는 디자이너 업무 기준 체감 추정치입니다. 정확한 통계가 아닙니다.</p>
    <p>사내 시범 운영에서 같은 인원이 하루에 만드는 장표가 늘었고, 톤을 맞추는 단순 작업에 드는 시간이 줄었습니다. 계속 측정하며 실제 수치로 바꿔 가고 있습니다.</p>
  </div>
  <div class="effect">
    <div class="effect__c">
      <p class="effect__l">01 · 장표 제작량 — 1인 · 하루</p>
      <p class="effect__v">약 4장 → <b>약 8장</b></p>
      <div class="bench">
        <div class="brow"><div class="brow__n">기존</div>
          <div class="brow__t"><i style="width:50%"></i></div>
          <div class="brow__v">4장 정도</div></div>
        <div class="brow brow--hi"><div class="brow__n">현재</div>
          <div class="brow__t"><i style="width:100%"></i></div>
          <div class="brow__v">8장 정도</div></div>
      </div>
      <p class="effect__n"><b>약 2배.</b> 소스 사이트와 지난 제안서를 뒤지던 시간이 줄었습니다.</p>
    </div>
    <div class="effect__c">
      <p class="effect__l">02 · 톤 정리 · 폰트 변경 등 단순 작업</p>
      <p class="effect__v">3명 · 하루 종일 → <b>3시간</b></p>
      <div class="bench">
        <div class="brow"><div class="brow__n">기존</div>
          <div class="brow__t"><i style="width:100%"></i></div>
          <div class="brow__v">3명이 하루 종일</div></div>
        <div class="brow brow--hi"><div class="brow__n">이번 테스트</div>
          <div class="brow__t"><i style="width:38%"></i></div>
          <div class="brow__v">처음이라 3시간</div></div>
      </div>
      <p class="effect__n"><b>하루 → 3시간.</b> 처음 해 본 테스트 결과라, 반복할수록 더 줄어들 것으로 봅니다.</p>
    </div>
  </div>
</div></section>

<section class="band"><div class="frame">
  <div class="head">
    <p class="kicker">Use cases</p>
    <h2>쌓인 자산은 이렇게 쓰입니다.</h2>
  </div>
  <div class="cases">
    <div class="case case--hi"><div class="case__g"><span>POWERPLUS FOR</span><span>제안서</span></div>
      <p><b>수주 제안서</b> 표지·간지·본문을 지난 제안서에서 꺼내 쓰고, 기관 로고와 아이콘으로 톤을 맞춥니다.</p></div>
    <div class="case"><div class="case__g"><span>POWERPLUS FOR</span><span>사내 보고</span></div>
      <p><b>주간·월간 보고</b> 다이어그램과 차트 아이콘으로 구조를 세우고 같은 서식으로 반복합니다.</p></div>
    <div class="case"><div class="case__g"><span>POWERPLUS FOR</span><span>교육 자료</span></div>
      <p><b>사내 교육·온보딩</b> 장면 일러스트로 설명을 붙이고, 배경 사진으로 표지를 만듭니다.</p></div>
    <div class="case"><div class="case__g"><span>POWERPLUS FOR</span><span>영업 자료</span></div>
      <p><b>고객 미팅</b> 자주 쓰는 장표를 즐겨찾기에 두고 현장에서 바로 꺼내 씁니다.</p></div>
    <div class="case"><div class="case__g"><span>POWERPLUS FOR</span><span>브랜드 통일</span></div>
      <p><b>디자인 일관성</b> 같은 스타일 세트로 한 장 안의 아이콘 톤을 맞춥니다.</p></div>
    <div class="case"><div class="case__g"><span>POWERPLUS FOR</span><span>자산 운영</span></div>
      <p><b>관리자</b> 무엇이 쓰이고 무엇을 못 찾았는지 보고 다음에 채울 자산을 정합니다.</p></div>
  </div>
</div></section>

<section class="band"><div class="frame">
  <div class="head">
    <p class="kicker">Roadmap</p>
    <h2>지금은 사람이 찾아 넣고,<br><b>다음은 시스템이 넣습니다.</b></h2>
    <p>자산이 쌓이고 무엇이 쓰이는지가 남으면, 다음은 그 자리에 맞는 자산을 시스템이 고르는 단계입니다. 같은 인원으로 더 많이, 품질은 일정하게 만드는 것이 목표입니다.</p>
  </div>
  <div class="cases">
    <div class="case"><div class="case__g"><span>Stage 01 · 운영 중</span><span>사람이 찾아 넣는다</span></div>
      <p>작업창에서 한국어로 검색하고 눌러서 넣습니다. 지금 회사에서 쓰고 있는 방식입니다.</p></div>
    <div class="case"><div class="case__g"><span>Stage 02 · 시험 중</span><span>AI 가 1차 가공</span></div>
      <p>장표 초안을 읽고 자리에 맞는 자산을 골라 넣으면서 아이콘과 톤, 폰트를 맞춥니다. 사람은 부족한 데만 손봅니다.</p></div>
    <div class="case case--hi"><div class="case__g"><span>Stage 03 · 목표</span><span>완전 자동화</span></div>
      <p>초안만 넣으면 완성 장표까지. 디자이너는 만드는 사람이 아니라 확인하고 다듬는 사람이 됩니다.</p></div>
  </div>
</div></section>
"""


# ══════════════════════════════════════════════════════════ FEATURES
FEATURES = """
<section class="hero hero--plain">
  <h1>흩어진 자료를 쌓고,<br><b>하나의 톤으로 꺼내 씁니다.</b></h1>
  <p class="sub">자산을 모으는 라이브러리, 쌓인 것을 찾아내는 한국어 검색, 서식째 넣는 장표 삽입. 세 가지가 파워포인트 작업창 안에서 한 번에 돌아갑니다.</p>
  <div class="hero__cta">
    <a class="btn btn--d" href="__MAIL__">무료로 시작</a>
    <a class="btn btn--s" href="{{DOCS}}">사용 설명서</a>
  </div>
</section>

<section class="band" id="library"><div class="frame">
  <div class="head">
    <p class="kicker">Library</p>
    <h2>제안서가 끝나도<br><b>자산은 남습니다.</b></h2>
    <p>나간 제안서를 낱장으로 잘라 등록하고 아이콘·사진·일러스트·로고를 카테고리와 주제로 나눠 담습니다. 자산 하나에 국문 25개·영문 25개 키워드를 붙여 다음 사람이 찾을 수 있게 합니다.</p>
  </div>
  <div class="tri">
    <div class="tri__c">
      <img src="shots/shot-illust.jpg" alt="일러스트 카테고리 화면" loading="lazy">
      <p><b>장면 단위 분류</b> 인물·회의·발표·분석처럼 실제로 쓰이는 장면으로 나눠 두어 카테고리만 눌러도 찾힙니다.</p>
    </div>
    <div class="tri__c">
      <img src="shots/shot-logo-full.jpg" alt="로고 카테고리 화면" loading="lazy">
      <p><b>기관 성격별 로고</b> 정부 부처·지자체·공단·진흥원으로 한 번 더 좁혀 제안서에 맞는 로고를 바로 꺼냅니다.</p>
    </div>
    <div class="tri__c">
      <img src="shots/shot-set.jpg" alt="같은 스타일 세트 화면" loading="lazy">
      <p><b>같은 스타일 세트</b> 색감·채도·밝기를 실측해 같은 결의 자산만 모읍니다. 한 장 안의 톤이 어긋나지 않습니다.</p>
    </div>
  </div>
</div></section>

<section class="band" id="search"><div class="frame">
  <div class="head">
    <p class="kicker">Korean search</p>
    <h2>오타를 써도,<br>이름을 몰라도 <b>찾아냅니다.</b></h2>
    <p>자산 쪽 태그를 늘리는 대신 검색어 쪽을 고칩니다. 자모 단위로 풀어 오타를 교정하고, 동의어·한↔영 사전과 조사·어미까지 함께 봅니다.</p>
  </div>
  <div class="qb">
    <div class="qb__h">Query correction — live behavior</div>
    <div class="qr"><span class="qi">코그</span><span class="qo"><b>‘코드’</b>로 고쳐서 찾았어요 · <em>38개</em></span></div>
    <div class="qr"><span class="qi">아이큰</span><span class="qo"><b>아이콘</b>으로 교정 · <em>1,586개</em></span></div>
    <div class="qr"><span class="qi">디비</span><span class="qo"><b>데이터베이스</b>와 같은 결과 · <em>124개</em></span></div>
    <div class="qr"><span class="qi">사람들</span><span class="qo">어간까지 넓혀서 · <em>243개</em></span></div>
  </div>

  <div class="head head--left" style="margin-top:120px;">
    <p class="kicker">Zero-result rate</p>
    <h2>못 찾은 검색어가<br><b>다음에 채울 목록이 됩니다.</b></h2>
    <p>결과가 하나도 안 나온 검색어는 실패 기록이 아니라, 다음에 무엇을 만들어야 하는지 직원들이 직접 알려 준 목록입니다. 지금까지 모인 <b>213개</b>를 우선순위로 삼아 자산을 채우고 있습니다.</p>
  </div>
  <div class="bench" style="max-width:920px;margin-inline:auto;">
    <div class="brow">
      <div class="brow__n">8월<span>검색 1,685건</span></div>
      <div class="brow__t"><i style="width:18.2%"></i></div>
      <div class="brow__v">18.2%</div>
    </div>
    <div class="brow brow--hi">
      <div class="brow__n">9월<span>검색 131건</span></div>
      <div class="brow__t"><i style="width:9.9%"></i></div>
      <div class="brow__v">9.9%</div>
    </div>
  </div>
  <p style="max-width:920px;margin:18px auto 0;font-size:13px;color:var(--ink-3);font-weight:400;">막대는 검색 중 결과가 0건이었던 비율입니다. 낮을수록 좋습니다. 9월은 표본이 131건으로 작아 아직 추세로 보기는 이릅니다. 관리자 화면의 무결과율 카드는 최근 30일 기준이라 이 월별 값과 다르게 나옵니다.</p>
</div></section>

<section class="band" id="decks"><div class="frame">
  <div class="split">
    <div>
      <p class="kicker">Decks · 731</p>
      <h2>지난 제안서가<br><b>낱장으로 쌓입니다.</b></h2>
      <p>나간 제안서를 표지·목차·간지·본문으로 잘라 등록합니다. 카드를 누르면 지금 선택한 슬라이드 뒤에 원본 서식 그대로 들어갑니다.</p>
      <ul class="list">
        <li><i aria-hidden="true"></i><span><b>서식 유지</b> — 글꼴과 색, 도형이 원본 그대로 옮겨집니다.</span></li>
        <li><i aria-hidden="true"></i><span><b>낱장·묶음</b> — 표지 한 장만, 또는 제안서 한 벌 전체.</span></li>
        <li><i aria-hidden="true"></i><span><b>권한 안에서만</b> — 사내 메일로 인증한 계정만 열람합니다.</span></li>
      </ul>
    </div>
    <div class="split__v"><img src="shots/shot-set.jpg" alt="powerPlus 장표 세트 화면" loading="lazy"></div>
  </div>
</div></section>

<section class="band" id="admin"><div class="frame">
  <div class="split split--f">
    <div>
      <p class="kicker">Access &amp; analytics</p>
      <h2>무엇이 쓰이는지<br><b>남습니다.</b></h2>
      <p>회사 메일로 인증한 계정만 들어오고, 권한 밖 자산은 목록에도 뜨지 않습니다. 무엇이 언제 쓰였는지가 남아 다음에 채울 자산이 정해집니다.</p>
      <ul class="list">
        <li><i aria-hidden="true"></i><span><b>재사용 78%</b> — 상위 3명이 전체 삽입의 78%. 한 번 쓴 사람은 계속 씁니다.</span></li>
        <li><i aria-hidden="true"></i><span><b>관리자 대시보드</b> — 인기 자산과 무결과 검색어를 한 화면에서.</span></li>
        <li><i aria-hidden="true"></i><span><b>요청 루프</b> — 없는 자료는 그 자리에서 요청으로 넘어갑니다.</span></li>
      </ul>
    </div>
    <div class="split__v"><img src="shots/shot-logo-full.jpg" alt="powerPlus 로고 카테고리 화면" loading="lazy"></div>
  </div>
</div></section>

<section class="band"><div class="frame">
  <div class="head">
    <p class="kicker">Comparison</p>
    <h2>지금 방식과 무엇이 다른가.</h2>
  </div>
  <div class="cmp">
    <table>
      <thead><tr>
        <th></th>
        <th><b>powerPlus</b>작업창</th>
        <th><b>공유 폴더</b>파일 서버</th>
        <th><b>웹 검색</b>외부 사이트</th>
      </tr></thead>
      <tbody>
        <tr><td>작업이 끝난 뒤에도 자산이 회사에 남음</td><td>__CK__</td><td>__CK__</td><td>__CX__</td></tr>
        <tr><td>여러 사람이 써도 톤이 유지됨</td><td>__CK__</td><td>__CX__</td><td>__CX__</td></tr>
        <tr><td>파워포인트를 떠나지 않고 삽입</td><td>__CK__</td><td>__CX__</td><td>__CX__</td></tr>
        <tr><td>한국어 키워드로 검색</td><td>__CK__</td><td>__CX__</td><td>__CK__</td></tr>
        <tr><td>오타·동의어 교정</td><td>__CK__</td><td>__CX__</td><td>__CK__</td></tr>
        <tr><td>지난 제안서 장표를 낱장으로</td><td>__CK__</td><td>__CX__</td><td>__CX__</td></tr>
        <tr><td>라이선스가 확인된 자산</td><td>__CK__</td><td>__CX__</td><td>__CX__</td></tr>
        <tr><td>회사 도메인 인증으로 접근 제한</td><td>__CK__</td><td>__CK__</td><td>__CX__</td></tr>
        <tr><td>무엇이 쓰였는지 기록</td><td>__CK__</td><td>__CX__</td><td>__CX__</td></tr>
      </tbody>
    </table>
  </div>
</div></section>
"""


# ══════════════════════════════════════════════════════════ USE CASES
USECASES = """
<section class="hero hero--plain">
  <h1>쌓인 자산이<br>어디에 쓰이는가.</h1>
  <p class="sub">한 번 쌓아 둔 라이브러리가 업무마다 어떻게 쓰이는지, 사내 시범 운영에서 실제로 쓰인 방식으로 정리했습니다.</p>
</section>

<section class="band"><div class="frame">
  <div class="cases" style="margin-top:0;">
    <div class="case case--hi"><div class="case__g"><span>POWERPLUS FOR</span><span>제안서</span></div>
      <p><b>수주 제안서</b> 표지·목차·간지를 지난 제안서에서 꺼내 쓰고, 발주 기관 로고와 업무 아이콘으로 톤을 맞춥니다. 서식이 그대로 따라와 내용만 고쳐 쓰면 됩니다.</p></div>
    <div class="case"><div class="case__g"><span>POWERPLUS FOR</span><span>사내 보고</span></div>
      <p><b>주간·월간 보고</b> 다이어그램과 차트 아이콘으로 구조를 세웁니다. 즐겨찾기에 둔 서식으로 매주 같은 모양을 반복합니다.</p></div>
    <div class="case"><div class="case__g"><span>POWERPLUS FOR</span><span>교육 자료</span></div>
      <p><b>사내 교육·온보딩</b> 장면 일러스트로 설명을 붙이고 배경 사진으로 표지를 만듭니다. 인물 일러스트 378종에서 상황에 맞는 것을 고릅니다.</p></div>
    <div class="case"><div class="case__g"><span>POWERPLUS FOR</span><span>영업 자료</span></div>
      <p><b>고객 미팅</b> 자주 쓰는 장표를 즐겨찾기에 두고 현장에서 바로 꺼냅니다. 최근 탭에 지난번에 쓴 자산이 그대로 남습니다.</p></div>
    <div class="case"><div class="case__g"><span>POWERPLUS FOR</span><span>브랜드 통일</span></div>
      <p><b>디자인 일관성</b> 같은 스타일 세트로 한 장 안의 아이콘 톤을 맞춥니다. 색감·채도·밝기를 실측해 묶어 둔 세트라 섞이지 않습니다.</p></div>
    <div class="case"><div class="case__g"><span>POWERPLUS FOR</span><span>자산 운영</span></div>
      <p><b>관리자</b> 무엇이 쓰였고 무엇을 못 찾았는지 대시보드에서 봅니다. 무결과 검색어가 다음에 채울 자산의 우선순위가 됩니다.</p></div>
  </div>
</div></section>

<section class="band"><div class="frame">
  <div class="head">
    <p class="kicker">In production</p>
    <h2>시범 운영에서 나온 숫자.</h2>
    <p>사내 ~300명 조직에서 실제로 측정한 값입니다. <b>2026년 9월 중순 기준</b>이며, 도입 효과를 가늠하는 기준으로 보시면 됩니다.</p>
  </div>
  <div class="stats" style="margin-top:56px;border-bottom:1px solid var(--hair);">
    <div><b>3,734</b><span>등록 자산</span></div>
    <div><b>746</b><span>누적 삽입</span></div>
    <div><b>1,823</b><span>누적 검색</span></div>
    <div><b>9.9%</b><span>무결과율 · 9월</span></div>
    <div><b>78%</b><span>상위 3명 비중</span></div>
    <div><b>213</b><span>못 찾은 검색어</span></div>
  </div>
  <p class="lede">가장 중요한 숫자는 <b>78%</b>입니다. 상위 3명이 전체 삽입의 78%를 차지했습니다. 한 번 손에 익은 사람은 계속 쓴다는 뜻이라, 도입 초기에는 자주 쓰는 사람이 찾는 자산부터 채우는 편이 효과가 큽니다.</p>
</div></section>
"""


# ══════════════════════════════════════════════════════════ PRICING
PRICING = """
<section class="hero hero--plain">
  <h1>무료로 시작하고,<br><b>필요할 때 올리세요.</b></h1>
  <p class="sub">모든 플랜에 라이브러리 전체와 파워포인트 추가 기능이 들어갑니다.</p>
  <div class="toggle" role="group" aria-label="결제 주기">
    <button type="button" data-cycle="m" class="on" aria-pressed="true">월 결제</button>
    <button type="button" data-cycle="y" aria-pressed="false">연 결제 −20%</button>
  </div>
  <p class="hero__note">아래 금액은 구조를 보여 주기 위한 예시이며 확정 전입니다.</p>
</section>

<section class="band"><div class="frame">
  <div class="plans" style="margin-top:0;">
    <div class="pl">
      <p class="pl__n">Team <span>· 제안서를 직접 만드는 소규모 팀</span></p>
      <p class="pl__p"><b data-m="29,000" data-y="23,200">29,000</b><span data-m="원 / 사용자·월" data-y="원 / 사용자·월 · 연 결제">원 / 사용자·월</span></p>
      <ul>
        <li>__CK__<span>기본 라이브러리 <b>전체 이용</b></span></li>
        <li>__CK__<span>자체 자산 업로드 500개</span></li>
        <li>__CK__<span>즐겨찾기 · 최근 사용 동기화</span></li>
        <li>__CK__<span>이메일 지원</span></li>
      </ul>
      <a class="btn btn--s" href="__MAIL__">14일 무료로 시작</a>
    </div>
    <div class="pl">
      <p class="pl__n">Business <span>· 전사에 배포하는 기업</span></p>
      <p class="pl__p"><b data-m="19,000" data-y="15,200">19,000</b><span data-m="원 / 사용자·월" data-y="원 / 사용자·월 · 연 결제">원 / 사용자·월</span></p>
      <ul>
        <li>__CK__<span>Team의 모든 기능</span></li>
        <li>__CK__<span>자체 자산 <b>무제한</b> · 대량 등록</span></li>
        <li>__CK__<span><b>관리자 대시보드</b> · 무결과 검색어</span></li>
        <li>__CK__<span>도메인 인증 · 부서별 권한</span></li>
        <li>__CK__<span>Office Store 전사 배포 지원</span></li>
      </ul>
      <a class="btn btn--d" href="__MAIL__">14일 무료로 시작</a>
    </div>
    <div class="pl">
      <p class="pl__n">Studio <span>· 자산을 제작해 납품하는 조직</span></p>
      <p class="pl__p"><b data-m="문의" data-y="문의">문의</b><span data-m="· 규모별 산정" data-y="· 규모별 산정">· 규모별 산정</span></p>
      <ul>
        <li>__CK__<span>Business의 모든 기능</span></li>
        <li>__CK__<span><b>자산 제작 대행</b> — 무결과 목록 기반</span></li>
        <li>__CK__<span>브랜드 가이드 반영 세트 구성</span></li>
        <li>__CK__<span>전담 담당자 배정</span></li>
      </ul>
      <a class="btn btn--s" href="__MAIL__">상담 요청</a>
    </div>
  </div>
</div></section>

<section class="band" id="selfhost"><div class="frame frame--tight">
  <div class="ent">
    <p class="kicker">Self-hosted</p>
    <h3>서버를 직접 두셔야 한다면.</h3>
    <p>자산이 외부로 나가면 안 되는 조직을 위한 방식입니다. 서버 한 대에 PHP와 MySQL이면 동작하므로 고객사 인프라에 그대로 올릴 수 있습니다.</p>
    <a class="btn btn--d" style="margin-top:26px;" href="__MAIL__">구축형 문의</a>
    <ul>
      <li>__CK__<span>고객사 서버에 설치하고 자산은 사내 망 안에만 둡니다.</span></li>
      <li>__CK__<span>구성은 보안 검토 결과에 따라 조정합니다.</span></li>
      <li>__CK__<span>설치, 초기 자산 이관, 관리자 교육까지 포함해 산정합니다.</span></li>
      <li>__CK__<span>전사 배포와 Office Store 등록을 함께 진행합니다.</span></li>
    </ul>
  </div>
</div></section>

<section class="band"><div class="frame">
  <div class="head">
    <p class="kicker">FAQ</p>
    <h2>도입 전에 가장 많이 듣는 것들.</h2>
  </div>
  <div class="faq">
    <div class="fi"><p class="fq">직원들에게 어떻게 배포하나요?</p><p class="fa">두 가지입니다. 지금은 <b>설치 파일을 받아 실행</b>하는 방식이라, 회사에 따라 백신 예외 처리가 한 번 필요하고 구버전 Office 를 쓰는 PC 가 걸러집니다. <b>Office Store 로 전사 배포</b>하면 직원은 파워포인트 안에서 내려받기만 하면 되고, 백신과 설치 부담이 함께 없어집니다. 업데이트도 심사를 거친 버전으로 자동 반영됩니다.</p></div>
    <div class="fi"><p class="fq">맥에서도 되나요?</p><p class="fa">됩니다. 추가 기능 본체를 웹 표준으로 만들어서 맥 파워포인트에서도 같은 작업창이 열립니다. Office Store를 통해 배포하면 윈도우와 맥 구분 없이 파워포인트 안에서 내려받습니다.</p></div>
    <div class="fi"><p class="fq">오래된 Office를 쓰는 직원이 있습니다.</p><p class="fa">Office 2019 이상이 필요합니다. 2016 이하는 내부 엔진이 달라 작업창이 열리지 않고, 설치 단계에서 미리 감지해 안내합니다. 도입 전에 라이선스 현황을 함께 확인해 드립니다.</p></div>
    <div class="fi"><p class="fq">기존에 쓰던 자료를 옮길 수 있나요?</p><p class="fa">폴더째 넘겨 주시면 일괄로 등록합니다. 이미지는 크기를 맞추고 키워드를 붙이며, 지난 제안서는 표지·목차·간지·본문 낱장으로 잘라 등록합니다. 옮기는 작업은 도입 과정에 포함됩니다.</p></div>
    <div class="fi"><p class="fq">자료가 외부 서버에 올라가는 게 걱정됩니다.</p><p class="fa">구독형은 회사 도메인 인증을 거친 계정만 접근하고 권한 밖 자산은 목록에도 뜨지 않습니다. 그래도 외부에 둘 수 없다면 구축형으로 고객사 서버에 설치합니다.</p></div>
    <div class="fi"><p class="fq">자산 저작권은 어떻게 되나요?</p><p class="fa">기본 라이브러리는 라이선스를 확인한 자산으로만 구성합니다. 고객사가 별도로 계약한 콘텐츠를 올리는 경우, 그 이용 범위는 계약 내용을 함께 확인한 뒤 반영합니다.</p></div>
    <div class="fi"><p class="fq">직원들이 실제로 쓸까요?</p><p class="fa">쓰는 사람이 쓰는 도구입니다. 사내 시범 운영에서는 상위 3명이 전체 삽입의 78%를 차지했습니다. 한 번 손에 익으면 계속 쓰기 때문에, 처음 한 달은 자주 쓰는 자산을 채우는 데 집중하는 편이 효과가 큽니다.</p></div>
  </div>
</div></section>

<script>
(function(){
  var bar = document.querySelector(".toggle");
  if (!bar) return;
  var btns = [].slice.call(bar.querySelectorAll("[data-cycle]"));
  var cells = [].slice.call(document.querySelectorAll(".pl__p [data-m]"));
  var rows  = [].slice.call(document.querySelectorAll(".pl__p"));

  function apply(cycle){
    btns.forEach(function(b){
      var on = b.dataset.cycle === cycle;
      b.classList.toggle("on", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
    cells.forEach(function(el){
      el.textContent = cycle === "y" ? el.dataset.y : el.dataset.m;
    });
  }

  btns.forEach(function(b){
    b.addEventListener("click", function(){
      var cycle = b.dataset.cycle;
      // 숫자가 바뀌는 순간을 살짝 눌러 줘서 변경을 알아채게 한다
      rows.forEach(function(r){ r.classList.add("is-swap"); });
      window.setTimeout(function(){
        apply(cycle);
        rows.forEach(function(r){ r.classList.remove("is-swap"); });
      }, 120);
    });
  });

  apply("m");
})();
</script>
"""

PAGES = [
    ('index.html',    'powerPlus',            '파워포인트 작업창에서 회사 자산을 검색해 클릭 한 번으로 슬라이드에 넣는 추가 기능.', 'home',     HOME),
    ('features.html', 'powerPlus — 기능',      '라이브러리·한국어 검색·장표 삽입. powerPlus의 기능을 화면과 함께 정리했습니다.',   'features', FEATURES),
    ('usecases.html', 'powerPlus — 활용 사례', '제안서·사내 보고·교육 자료 등 업무별 powerPlus 활용 방식과 운영 지표.',          'usecases', USECASES),
    ('pricing.html',  'powerPlus — 요금제',    'Team·Business·Studio 플랜과 구축형 안내, 도입 전 자주 묻는 질문.',              'pricing',  PRICING),
]

here = os.path.dirname(os.path.abspath(__file__))
for fn, title, desc, active, body in PAGES:
    body = (body.replace('__WALL__', WALL).replace('__MAIL__', MAIL)
                .replace('__CK__', CHECK).replace('__CX__', CROSS))
    sky = '__NAV__' in body
    if sky:                      # 홈 — 내비를 하늘 카드 안으로 넣는다
        body = body.replace('__NAV__', nav(active))
    io.open(os.path.join(here, fn), 'w', encoding='utf-8', newline='').write(
        page(title, desc, active, body, sky=sky))
    print('built', fn)
