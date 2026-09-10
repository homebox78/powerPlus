# -*- coding: utf-8 -*-
"""아이콘(PPICON) ↔ 우측 텍스트 블록 세로 중심 — 전수 실측 후 정렬. 인자: <src> <dst> [apply]"""
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); APPLY = len(sys.argv) > 3
SKIP = {21}; IN = 72.0; TOL = 0.03 * IN
app = win32.Dispatch("PowerPoint.Application"); pres = app.Presentations.Open(src, WithWindow=False)
def sh_of(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i); o += sh_of(s.GroupItems) if s.Type == 6 else [s]
    return o
bad_before, fixed, skipped = [], 0, []
try:
    for sno in range(1, pres.Slides.Count + 1):
        if sno in SKIP: continue
        shapes = sh_of(pres.Slides(sno).Shapes)
        icons = [s for s in shapes if s.Name == "PPICON"]
        texts = [s for s in shapes if s.HasTextFrame and s.TextFrame.HasText and s.Name != "PPICON"
                 and s.Height <= 2.0 * IN and s.Width <= 8 * IN]
        for ic in icons:
            L, T, W, H = ic.Left, ic.Top, ic.Width, ic.Height; R, B = L + W, T + H; cy = T + H / 2
            near = []
            for t in texts:
                gap = t.Left - R
                if not (-W * 0.25 <= gap <= 0.8 * IN): continue
                tr = t.TextFrame.TextRange
                try: bt, bh = tr.BoundTop, tr.BoundHeight
                except Exception: continue
                if bt + bh < T - 0.3 * IN or bt > B + 0.3 * IN: continue     # 세로로 겹치는 범위만
                if t.Width < 0.5 * IN and len(tr.Text.strip()) <= 3: continue  # 번호 뱃지류 제외
                near.append((bt, bt + bh))
            if not near: continue
            top, bot = min(n[0] for n in near), max(n[1] for n in near)
            d = (top + bot) / 2 - cy
            if abs(d) > TOL:
                bad_before.append((sno, round(d / IN, 2)))
                if abs(d) > 0.35 * IN: skipped.append((sno, round(d / IN, 2))); continue
                if APPLY: ic.Top += d; fixed += 1
    from collections import Counter
    print(f"어긋남(>0.03in) {len(bad_before)}곳: {dict(Counter(s for s,_ in bad_before))}")
    print(f"큰 편차로 건너뜀 {len(skipped)}: {skipped}")
    if APPLY: print("정렬:", fixed); pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
