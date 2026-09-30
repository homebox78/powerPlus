# -*- coding: utf-8 -*-
"""그림 교체 준비 — COM 이름(Picture N, 영문)과 XML 이름(그림 N, 한글)이 달라 set_swap 지정표를 바로 못 쓴다.
   COM 으로 대상 그림에 고유 이름(SW00…)을 붙여 SaveCopyAs 하고, 그 이름으로 set_swap 지정표를 만든다.
   그룹 안 그림도 이름만 바뀌므로 그룹 구조가 유지된다.
   인자: <src.pptx> <dst.pptx> <picks.json> <spec_out.json> <lib_dir>
   picks = [[슬라이드, "COM 이름", 자산id, "메모"], ...]  (같은 이름이 여럿이면 가장 큰 것)"""
import json, os, sys
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst, picks, out, lib = [os.path.abspath(a) for a in sys.argv[1:6]]
P = json.load(open(picks, encoding="utf-8"))
app = win32.Dispatch("PowerPoint.Application")
pr = app.Presentations.Open(src, ReadOnly=False, WithWindow=False)


def flat(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i)
        o += flat(s.GroupItems) if s.Type == 6 else [s]
    return o


spec = []
for k, (sno, nm, iid, _) in enumerate(P):
    hits = [s for s in flat(pr.Slides(sno).Shapes) if s.Name == nm and s.Type == 13]
    if not hits:
        print("없음", sno, nm); continue
    s = max(hits, key=lambda x: x.Width * x.Height)
    s.Name = f"SW{k:02d}"
    spec.append([sno, s.Name, os.path.join(lib, f"illust_{iid}.png"), 0])
pr.SaveCopyAs(dst); pr.Close()
json.dump(spec, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print("지정", len(spec), "/", len(P), "→ set_swap.py", dst, "<out.pptx>", out)
