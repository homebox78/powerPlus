# -*- coding: utf-8 -*-
"""도식 화살표·연결선만 골라 굵기·투명도를 한 값으로(기본 0.5pt · 투명도 25%).
   바꾸는 것: 화살촉이 있는 선 · 도형에 붙은 연결선 · 점선 연결 · 도식 장표(DIAG)의 흐름선
   두는 것: 그라데이션 선 · 굵은 둥근점선(… 말줄임) · 3pt 이상 화살촉 없는 선(괄호·막대·금지 사선) ·
            옅은 구분선(투명도 70%↑, 화살촉 없음) · 표 · 기획 메모
   인자: <src> <dst> [굵기pt=0.5] [투명도=0.25] [dry]"""
import os, sys, time, collections
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
W = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
TR = float(sys.argv[4]) if len(sys.argv) > 4 else 0.25
DRY = "dry" in sys.argv
DIAG = {7, 13, 16, 20, 21, 22, 23, 24, 25, 27, 28, 31, 32, 33}
app = win32.Dispatch("PowerPoint.Application"); pres = app.Presentations.Open(src, WithWindow=False)
def sh_of(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i); o += sh_of(s.GroupItems) if s.Type == 6 else [s]
    return o
done, skip = collections.Counter(), collections.Counter()
try:
    for sno in range(1, pres.Slides.Count + 1):
        for s in sh_of(pres.Slides(sno).Shapes):
            try:
                conn = s.Connector == -1
                line = s.Type == 9 or conn
                if not line and s.Type == 5:
                    line = s.Fill.Visible == 0
                if not line: continue
                ln = s.Line
                if ln.Visible != -1: continue
                arrow = ln.EndArrowheadStyle > 1 or ln.BeginArrowheadStyle > 1
                attached = conn and (s.ConnectorFormat.BeginConnected or s.ConnectorFormat.EndConnected)
                t = ln.Transparency
                why = None
                if t < -1 or t > 1: why = "그라데이션"
                elif ln.DashStyle == 11 and ln.Weight >= 3: why = "말줄임 점선"
                elif ln.Weight >= 2.9 and not arrow: why = "굵은 장식"
                elif t >= 0.7 and not arrow: why = "옅은 구분선"
                elif not (arrow or attached or ln.DashStyle != 1 or sno in DIAG): why = "도식 밖"
                elif sno == 13 and s.Name == "Straight Connector 228": why = "금지 사선"
                elif sno == 18 and s.Name == "자유형 114": why = "상자 테두리"
                if why: skip[why] += 1; continue
                if not DRY:
                    ln.Weight = W; ln.Transparency = TR
                done[sno] += 1
            except Exception: pass
    print("변경", sum(done.values()), dict(sorted(done.items())))
    print("둠", dict(skip))
    if not DRY: pres.SaveAs(dst)
finally:
    pres.Close(); time.sleep(0.3)
