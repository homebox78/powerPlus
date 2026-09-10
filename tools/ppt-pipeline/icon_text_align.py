# -*- coding: utf-8 -*-
"""아이콘(PPICON) 오른쪽 텍스트: 제목↔설명 간격 통일 + 아이콘을 텍스트 실측 중심에 세로 정렬."""
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
IN = 72.0; GAP_PT = 2.0          # 제목→설명 간격(포인트)
app = win32.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(src, WithWindow=False)
def sh_of(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i); o += sh_of(s.GroupItems) if s.Type == 6 else [s]
    return o
stat = {"center": 0, "gap1": 0, "gap2": 0}
try:
    for sno in range(1, pres.Slides.Count + 1):
        shapes = sh_of(pres.Slides(sno).Shapes)
        icons = [s for s in shapes if s.Name == "PPICON"]
        texts = [s for s in shapes if s.HasTextFrame and s.TextFrame.HasText and s.Name != "PPICON"]
        for ic in icons:
            L, T, W, H = ic.Left, ic.Top, ic.Width, ic.Height
            R, B = L + W, T + H
            near = []
            for t in texts:
                if t.Height > 1.3 * IN or t.Width > 6 * IN: continue
                gap = t.Left - R
                if not (-W * 0.3 <= gap <= 0.6 * IN): continue
                tr = t.TextFrame.TextRange
                try: bt, bh = tr.BoundTop, tr.BoundHeight
                except Exception: continue
                if bt + bh < T - 0.15 * IN or bt > B + 0.15 * IN: continue
                near.append((t, tr, bt, bh, tr.Font.Size))
            if not near: continue
            near.sort(key=lambda x: x[2])
            # 제목/설명 간격
            if len(near) == 1:
                t, tr, bt, bh, fs = near[0]
                if tr.Paragraphs().Count >= 2:
                    p1, p2 = tr.Paragraphs(1), tr.Paragraphs(2)
                    if p1.Font.Size > p2.Font.Size * 1.15:
                        p1.ParagraphFormat.SpaceAfter = 0
                        p2.ParagraphFormat.SpaceBefore = GAP_PT
                        stat["gap1"] += 1
            elif len(near) == 2:
                (t1, tr1, bt1, bh1, f1), (t2, tr2, bt2, bh2, f2) = near
                if f1 > f2 * 1.15:
                    want = bt1 + bh1 + GAP_PT; d = want - bt2
                    if abs(d) <= 0.12 * IN: t2.Top += d; stat["gap2"] += 1
            # 실측 텍스트 범위의 중심에 아이콘 세로 정렬
            tops = [x[1].BoundTop for x in near]; bots = [x[1].BoundTop + x[1].BoundHeight for x in near]
            cy = (min(tops) + max(bots)) / 2
            if abs((T + H / 2) - cy) > 0.5:
                ic.Top = cy - H / 2; stat["center"] += 1
    print(stat); pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
