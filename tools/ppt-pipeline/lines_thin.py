# -*- coding: utf-8 -*-
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); IN = 72.0
app = win32.Dispatch("PowerPoint.Application"); pres = app.Presentations.Open(src, WithWindow=False)
def sh_of(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i); o += sh_of(s.GroupItems) if s.Type == 6 else [s]
    return o
lines = {}
try:
    # ① 1pt 실선 → 0.75pt (표는 제외)
    for sno in range(1, pres.Slides.Count + 1):
        for s in sh_of(pres.Slides(sno).Shapes):
            if s.Type == 19: continue
            try:
                ln = s.Line
                if ln.Visible == -1 and ln.DashStyle == 1 and abs(ln.Weight - 1.0) < 0.06:
                    ln.Weight = 0.75; lines[sno] = lines.get(sno, 0) + 1
            except Exception: pass
    print("1pt→0.75pt:", sum(lines.values()), "개 /", len(lines), "슬라이드")
    # ② s22 진단 박스: 제목↔설명 여백 제거, 세 요소를 박스 중심에 세로 정렬
    shp = {s.Id: s for s in sh_of(pres.Slides(22).Shapes)}
    box, lab, t1, t2 = shp[117], shp[118], shp[119], shp[120]
    cy = box.Top + box.Height / 2
    r1, r2, rl = t1.TextFrame.TextRange, t2.TextFrame.TextRange, lab.TextFrame.TextRange
    t2.Top += (r1.BoundTop + r1.BoundHeight + 1) - r2.BoundTop          # 여백 1pt
    top = r1.BoundTop; bot = r2.BoundTop + r2.BoundHeight
    d = cy - (top + bot) / 2; t1.Top += d; t2.Top += d
    lab.Top += cy - (rl.BoundTop + rl.BoundHeight / 2)
    print(f"s22 진단: 박스중심 {cy/IN:.2f} 라벨중심 {(rl.BoundTop+rl.BoundHeight/2)/IN:.2f} 본문 {r1.BoundTop/IN:.2f}~{(r2.BoundTop+r2.BoundHeight)/IN:.2f}")
    # ③ s24 점선 박스: 안쪽 박스 둘레로 0.08in 여백
    shp = {s.Id: s for s in sh_of(pres.Slides(24).Shapes)}
    dot, a, b, cap = shp[111], shp[97], shp[100], shp[112]
    M = 0.08 * IN
    dot.Left = a.Left - M; dot.Top = a.Top - M
    dot.Width = (b.Left + b.Width) - a.Left + 2 * M; dot.Height = a.Height + 2 * M
    cap.Top = dot.Top + dot.Height + 0.02 * IN; cap.Left = dot.Left; cap.Width = dot.Width
    print(f"s24 점선: {dot.Left/IN:.2f},{dot.Top/IN:.2f} {dot.Width/IN:.2f}x{dot.Height/IN:.2f} 캡션 top {cap.Top/IN:.2f}")
    pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
