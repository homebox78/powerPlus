# -*- coding: utf-8 -*-
"""오늘 지시사항 체크리스트 자동 검수 — 항목별 위반 수와 위치를 출력. 인자: <pptx>"""
import collections, hashlib, io, os, re, sys, time, zipfile
import win32com.client as win32
from pptx import Presentation
from pptx.util import Emu
sys.stdout.reconfigure(encoding="utf-8")
src = os.path.abspath(sys.argv[1]); IN = 72.0; VT = chr(11); D = chr(8212)
R = collections.OrderedDict()
def add(k, v): R.setdefault(k, []).append(v)
# ── XML/python-pptx 계열 ──
pres = Presentation(src)
def walk(shs):
    for s in shs:
        if s.shape_type == 6: yield from walk(s.shapes)
        else: yield s
for sno, sl in enumerate(pres.slides, 1):
    c = collections.Counter(hashlib.sha1(s.image.blob).hexdigest() for s in sl.shapes if s.name == "PPICON")
    if sno != 21:
        for h, n in c.items():
            if n > 1: add("01 같은 슬라이드 중복 아이콘", (sno, n))
    icons = [s for s in sl.shapes if s.name == "PPICON"]
    if len(icons) >= 2:
        g = sorted((s.width * s.height) ** 0.5 / 914400 for s in icons)
        cl, cur = [], [g[0]]
        for a, b in zip(g, g[1:]):
            (cur.append(b) if b / a <= 1.6 else (cl.append(cur), cur := [b]))
        cl.append(cur)
        for x in cl:
            if len(x) >= 2 and max(x) / min(x) > 1.12: add("10 아이콘 덩어리감(무리 내 편차>12%)", (sno, round(max(x)/min(x), 2)))
z = zipfile.ZipFile(src)
for n in z.namelist():
    if not (n.startswith("ppt/slides/slide") and n.endswith(".xml")): continue
    sno = int(re.findall(r"slide(\d+)", n)[0]); x = z.read(n).decode("utf-8")
    b = len(re.findall(r'<a:rPr[^>]*\bb="1"', x))
    if b: add("08 볼드 효과 잔존", (sno, b))
    for m in re.finditer(r'<a:ln w="(\d+)"[^>]*>(.*?)</a:ln>', x, re.S):
        w = int(m.group(1)) / 12700; body = m.group(2)
        if "<a:solidFill>" in body and "prstDash" not in body:
            if abs(w - 0.75) > 0.05 and abs(w - 1.0) > 0.05 and w > 0.3: add("07a 실선 굵기(0.75/1 외)", (sno, round(w, 2)))
            if 'alpha val="70000"' not in body: add("07b 실선 알파 30% 아님", (sno, round(w, 2)))
    for m in re.finditer(r'<p:sp>.*?</p:sp>', x, re.S):
        sp = m.group(0)
        if 'prst="rightArrow"' in sp and "<a:gradFill" not in sp: add("11 오른쪽 화살표 그라데이션 없음", sno)
# ── COM 계열 ──
app = win32.Dispatch("PowerPoint.Application"); pp = app.Presentations.Open(src, WithWindow=False)
def sh_of(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i); o += sh_of(s.GroupItems) if s.Type == 6 else [s]
    return o
def texts_of(shapes):
    out = []
    for s in shapes:
        if s.HasTable == -1:
            t = s.Table
            for r in range(1, t.Rows.Count + 1):
                for c in range(1, t.Columns.Count + 1): out.append((s, t.Cell(r, c).Shape.TextFrame.TextRange))
        elif s.HasTextFrame and s.TextFrame.HasText: out.append((s, s.TextFrame.TextRange))
    return out
SP = set(" \t\r\n" + VT + chr(13))
try:
    for sno in range(1, pp.Slides.Count + 1):
        shapes = sh_of(pp.Slides(sno).Shapes); tx = texts_of(shapes)
        icons = [s for s in shapes if s.Name == "PPICON"]
        tshapes = [s for s, _ in tx if s.HasTextFrame]
        # 02 아이콘 ↔ 우측 텍스트 세로 중심
        if sno != 21:
            for ic in icons:
                L, T, W, H = ic.Left, ic.Top, ic.Width, ic.Height; R_, B = L + W, T + H
                near = []
                for t in tshapes:
                    if t.Height > 2 * IN or t.Width > 8 * IN: continue
                    gap = t.Left - R_
                    if not (-W * 0.25 <= gap <= 0.8 * IN): continue
                    tr = t.TextFrame.TextRange; bt, bh = tr.BoundTop, tr.BoundHeight
                    if bt + bh < T - 0.3 * IN or bt > B + 0.3 * IN: continue
                    if t.Width < 0.5 * IN and len(tr.Text.strip()) <= 3: continue
                    near.append((bt, bt + bh))
                if near:
                    d = (min(n[0] for n in near) + max(n[1] for n in near)) / 2 - (T + H / 2)
                    if 0.03 * IN < abs(d) <= 0.35 * IN: add("02 아이콘↔우측텍스트 세로중심 어긋남", (sno, round(d / IN, 2)))
        # 13 아이콘이 글자 위에 겹침(실측 글자 영역과 교차)
        for ic in icons:
            for t in tshapes:
                tr = t.TextFrame.TextRange
                try: bl, bt, bw, bh = tr.BoundLeft, tr.BoundTop, tr.BoundWidth, tr.BoundHeight
                except Exception: continue
                ox = min(ic.Left + ic.Width, bl + bw) - max(ic.Left, bl); oy = min(ic.Top + ic.Height, bt + bh) - max(ic.Top, bt)
                if ox > 0.06 * IN and oy > 0.06 * IN: add("13 아이콘이 글자와 겹침", (sno, tr.Text.strip()[:12]))
        for s, tr in tx:
            t = tr.Text
            if not t.strip(): continue
            # 05 한글 어절 중간 줄바꿈
            n = tr.Lines().Count
            for i in range(1, n):
                a = tr.Lines(i, 1); b = tr.Lines(i + 1, 1); e = a.Start + a.Length - 1; st = b.Start
                if e < 1 or st > len(t): continue
                if t[e - 1] not in SP and t[st - 1] not in SP and re.match(r"[가-힣]", t[st - 1]) and re.match(r"[가-힣]", t[e - 1]):
                    add("05 한글 어절 중간 잘림", (sno, t[max(0,e-4):st+3].replace("\r"," ")))
            # 04 고아 줄
            for pi in range(1, tr.Paragraphs().Count + 1):
                p = tr.Paragraphs(pi); ln = p.Lines().Count
                if ln >= 2 and len(p.Lines(ln, 1).Text.strip()) <= 1: add("04 고아 줄(마지막 1글자)", (sno, p.Text.strip()[:14]))
                # 06 대시 문단 2줄인데 대시 뒤 줄바꿈 없음
                pt = p.Text
                if D in pt and p.Lines().Count >= 2 and (pt.find(D) + 1 >= len(pt) or pt[pt.find(D) + 1] != VT): add("06 대시 뒤 줄바꿈 없음", (sno, pt.strip()[:16]))
            # 09 작은 글 서체
            for i in range(1, tr.Runs().Count + 1):
                r = tr.Runs(i); f = r.Font
                if f.Size <= 10 and re.search(r"[가-힣A-Za-z]", r.Text) and f.Name not in ("a시월구일2", "a시월구일3"):
                    add("09 작은 글 서체 규칙 위반", (sno, f.Name, r.Text.strip()[:10]))
        # 03 카드 내 콘텐츠 세로 중심(빈 카드 + 아이콘 + 텍스트)
        cards = [s for s in shapes if s.Type in (1, 5) and 0.6 * IN <= s.Height <= 2.0 * IN and s.Width >= 1.5 * IN and not (s.HasTextFrame and s.TextFrame.HasText)]
        for card in cards:
            def inside(s): cx, cy = s.Left + s.Width / 2, s.Top + s.Height / 2; return card.Left + 2 <= cx <= card.Left + card.Width - 2 and card.Top <= cy <= card.Top + card.Height
            mem = [s for s in shapes if s is not card and inside(s) and s.Width < card.Width * 0.98 and not (s.Type in (1, 5) and s.Width > 0.35 * IN and s.Height > 0.35 * IN and not (s.HasTextFrame and s.TextFrame.HasText))]
            ics = [s for s in mem if s.Name == "PPICON"]; tts = [s for s in mem if s.HasTextFrame and s.TextFrame.HasText and s.Width > 0.6 * IN and not (s.Width <= 0.35 * IN)]
            if not ics or not tts: continue
            tops = [s.TextFrame.TextRange.BoundTop for s in tts]; bots = [s.TextFrame.TextRange.BoundTop + s.TextFrame.TextRange.BoundHeight for s in tts]
            ic_top = min(i.Top for i in ics); ic_bot = max(i.Top + i.Height for i in ics)
            stacked = ic_bot <= min(tops) + 4
            top, bot = (min(ic_top, min(tops)), max(bots)) if stacked else (min(tops), max(bots))
            d = (card.Top + card.Height / 2) - (top + bot) / 2
            if 0.04 * IN < abs(d) <= 0.35 * IN: add("03 카드 내 콘텐츠 세로중심 어긋남", (sno, round(d / IN, 2)))
finally:
    pp.Close(); time.sleep(0.4)
print("=== 검수 결과", os.path.basename(src))
for k in sorted(R): print(f"[{k}] {len(R[k])}건 → {R[k][:12]}{' …' if len(R[k])>12 else ''}")
if not R: print("위반 0")
