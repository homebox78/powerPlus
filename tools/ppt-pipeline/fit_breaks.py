# -*- coding: utf-8 -*-
"""8-1 줄바꿈 정리 — 실제 렌더된 줄(TextRange.Lines)을 읽어 어절이 줄 중간에서 잘린 문단을 푼다.
   1순위: 문단 글자를 0.25pt 씩 줄여(최대 -2pt, 7pt 미만 금지) 잘림을 없앤다
   2순위: 잘린 어절 앞에 줄바꿈(chr 11)을 넣어 통째로 다음 줄로 보낸다
   3순위: 둘 다 안 되면 보고(도형을 넓히거나 문구를 줄여야 함)
   고아 줄(마지막 줄 1~2글자)도 1순위로 푼다.
   제외: 노란 기획 메모 · 분홍 '디자인' 말풍선 · 줄바꿈 안 하는 글상자 · 표.
   인자: <src> <dst> [report.json]"""
import os, sys, json, re
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
rep = sys.argv[3] if len(sys.argv) > 3 else None
SP = " \u00a0\t\r\n\v\u000b"
WORD = re.compile(r"[0-9A-Za-z\uac00-\ud7a3]")
MEMO_BGR = {0x00FFFF, 0xCCFFFF, 0x99FFFF, 0x87FFFF}   # FFFF00 FFFFCC FFFF99 FFFF87 (BGR)

app = win32.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(src, WithWindow=False)

def shapes(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i)
        try:
            o += shapes(s.GroupItems) if s.Type == 6 else [s]
        except Exception:
            o.append(s)
    return o

def is_memo(s):
    try:
        if s.Fill.Visible and s.Fill.Type == 1 and s.Fill.ForeColor.RGB in MEMO_BGR:
            return True
    except Exception:
        pass
    try:
        return "말풍선" in s.Name and "디자인" in s.TextFrame.TextRange.Text
    except Exception:
        return False

def breaks(p):
    """(잘린 줄 번호 목록, 고아 여부)"""
    n = p.Lines().Count
    bad = []
    for i in range(1, n):
        a, b = p.Lines(i, 1).Text, p.Lines(i + 1, 1).Text
        if not a or not b or a[-1] in SP or b[0] in SP:
            continue
        if WORD.match(a[-1]) and WORD.match(b[0]):
            bad.append(i)
    orphan = n >= 2 and len(p.Lines(n, 1).Text.strip()) <= 2 and len(p.Text.strip()) > 6
    return bad, orphan

def sizes(p):
    return [p.Runs(k).Font.Size for k in range(1, p.Runs().Count + 1)]

def set_sizes(p, ss):
    for k, v in enumerate(ss, 1):
        p.Runs(k).Font.Size = v

shrunk = []; wrapped = []; left = []
for sno in range(1, pres.Slides.Count + 1):
    for s in shapes(pres.Slides(sno).Shapes):
        try:
            if s.HasTable or not s.HasTextFrame or not s.TextFrame.HasText or is_memo(s):
                continue
            if s.TextFrame.WordWrap == 0:
                continue
        except Exception:
            continue
        tr = s.TextFrame.TextRange
        for pi in range(1, tr.Paragraphs().Count + 1):
            p = tr.Paragraphs(pi)
            if not p.Text.strip():
                continue
            try:
                bad, orph = breaks(p)
            except Exception:
                continue
            if not bad and not orph:
                continue
            base = sizes(p)
            ok = False
            for step in range(1, 9):            # 0.25 ~ 2.0pt
                ns = [v - 0.25 * step for v in base]
                if min(ns) < 7:
                    break
                set_sizes(p, ns)
                b2, o2 = breaks(p)
                if not b2 and not o2:
                    ok = True
                    shrunk.append((sno, s.Name, p.Text.strip()[:30], -0.25 * step))
                    break
            if ok:
                continue
            set_sizes(p, base)
            bad, orph = breaks(p)
            if bad:
                # 뒤쪽 줄부터 어절 앞에 줄바꿈 삽입(앞쪽 위치가 흔들리지 않게)
                done = 0
                for i in reversed(bad):
                    ln = p.Lines(i, 1)
                    t = ln.Text
                    cut = max(t.rfind(" "), t.rfind("\u00a0"))
                    if cut < 0:
                        continue                  # 한 어절이 줄보다 길다 → 보고
                    pos = ln.Start + cut          # 공백 자리(1-based Start 기준 cut 번째 다음 문자)
                    tr.Characters(pos, 1).Text = chr(11)
                    done += 1
                p = tr.Paragraphs(pi)
                b3, _ = breaks(p)
                if done and not b3:
                    wrapped.append((sno, s.Name, p.Text.strip()[:30]))
                else:
                    left.append((sno, s.Name, p.Text.strip()[:30], "어절이 줄보다 김"))
            elif orph:
                left.append((sno, s.Name, p.Text.strip()[:30], "고아 줄"))

pres.SaveAs(dst); pres.Close()
print("축소", len(shrunk), "· 어절 앞 줄바꿈", len(wrapped), "· 남김", len(left))
for x in left:
    print("  남김", x)
if rep:
    json.dump({"shrunk": shrunk, "wrapped": wrapped, "left": left}, open(rep, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
