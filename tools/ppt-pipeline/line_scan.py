# -*- coding: utf-8 -*-
"""줄바꿈 전수 점검(읽기 전용) — 실제 렌더 줄(TextRange.Lines)로
   ① 어절 중간 끊김 ② 1~2글자짜리 줄(중간·마지막) ③ 글상자 넘침 을 슬라이드별로 보고한다.
   기획 메모(노랑)·표는 제외. 인자: <pptx>"""
import os, re, sys
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src = os.path.abspath(sys.argv[1])
MEMO_BGR = {0x00FFFF, 0xCCFFFF, 0x99FFFF, 0x87FFFF}
WORD = re.compile(r"[0-9A-Za-z가-힣]")
app = win32.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(src, ReadOnly=True, WithWindow=False)


def shapes(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i)
        o += shapes(s.GroupItems) if s.Type == 6 else [s]
    return o


out = []
for sno in range(1, pres.Slides.Count + 1):
    for s in shapes(pres.Slides(sno).Shapes):
        try:
            if not s.HasTextFrame or not s.TextFrame.HasText:
                continue
            if s.Fill.Visible and s.Fill.Type == 1 and s.Fill.ForeColor.RGB in MEMO_BGR:
                continue
            if not s.TextFrame.WordWrap:
                continue
        except Exception:
            continue
        tf = s.TextFrame
        tr = tf.TextRange
        for i in range(1, tr.Paragraphs().Count + 1):
            p = tr.Paragraphs(i)
            n = p.Lines().Count
            if n < 2:
                continue
            L = [p.Lines(k, 1).Text for k in range(1, n + 1)]
            for k in range(n - 1):
                a, b = L[k], L[k + 1]
                if a and b and WORD.match(a[-1]) and WORD.match(b[0]) and not a.endswith(chr(11)):
                    out.append((sno, s.Name, "끊김", a.strip() + " | " + b.strip()))
            for k, ln in enumerate(L):
                t = ln.strip("  \r\n\x0b-•·").strip()
                if 0 < len(t) <= 2:
                    out.append((sno, s.Name, "짧은 줄" if k < n - 1 else "고아 줄", " / ".join(x.strip() for x in L)))
        try:
            if s.Height + 2 < tr.BoundHeight and tf.AutoSize == 0:
                out.append((sno, s.Name, "넘침", f"{tr.BoundHeight - s.Height:.1f}pt"))
        except Exception:
            pass
for o in out:
    print(*o)
print("합계", len(out))
pres.Close()
