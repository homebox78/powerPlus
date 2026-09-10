# -*- coding: utf-8 -*-
"""한글 어절이 줄 중간에서 잘리면 그 어절 앞에 줄바꿈을 넣어 통째로 다음 줄로 보낸다.
   PowerPoint 가 실제로 그린 줄(TextRange.Lines)을 읽으므로 폰트와 무관하게 정확하다.
   ⚠️ eaLnBrk 속성은 PowerPoint 가 무시한다 — 이 방법이 유일하다."""
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst, first = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), int(sys.argv[3])
SP = " \u00a0\t\r\n\v\u000b"

app = win32.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(src, WithWindow=False)
fixed = 0
try:
    for sno in range(first, pres.Slides.Count + 1):
        sl = pres.Slides(sno)
        def sh_of(c):
            o = []
            for i in range(1, c.Count + 1):
                s = c.Item(i)
                o += sh_of(s.GroupItems) if s.Type == 6 else [s]
            return o
        for sh in sh_of(sl.Shapes):
            try:
                if not sh.HasTextFrame:
                    continue
                tr = sh.TextFrame.TextRange
                if not tr.Text.strip():
                    continue
            except Exception:
                continue
            for _ in range(8):
                try:
                    txt = tr.Text
                    n = tr.Lines().Count
                except Exception:
                    break
                if n < 2:
                    break
                cut = None
                for i in range(1, n):
                    a = tr.Lines(i, 1); b = tr.Lines(i + 1, 1)
                    e = a.Start + a.Length - 1
                    s = b.Start
                    if e < 1 or s > len(txt) or e >= len(txt):
                        continue
                    c1, c2 = txt[e - 1], txt[s - 1]
                    if c1 in SP or c2 in SP:
                        continue                       # 공백에서 끊겼으면 정상
                    p = e
                    while p > 1 and txt[p - 2] not in SP:
                        p -= 1
                    if p <= a.Start:
                        continue                       # 어절이 한 줄보다 길다 — 못 고친다
                    cut = p
                    break
                if cut is None:
                    break
                try:
                    tr.Characters(cut, 0).InsertBefore(chr(11))
                    fixed += 1
                except Exception:
                    break
        if sno % 10 == 0:
            print(f"  …s{sno} (누적 {fixed})")
    pres.SaveAs(dst)
    print(f"어절 잘림 {fixed}곳 수정 → {os.path.basename(dst)}")
finally:
    pres.Close(); time.sleep(0.4)
