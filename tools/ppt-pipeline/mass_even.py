# -*- coding: utf-8 -*-
"""삽입한 아이콘·일러스트의 덩어리감 통일.
   ① (python-pptx) 지정한 그림의 투명 여백을 잘라 그림 틀 = 실제 그림 크기로
   ② (COM) 같은 장 · 같은 종류(인물/아이콘) · 크기가 비슷한 무리(인접 비 1.8 이내)끼리
      √(가로×세로)를 무리의 가운데 값으로. 인물은 발밑 가운데, 아이콘은 정가운데 고정. 배율 0.6~1.6. 같은 줄·같은 열로 나란한 것만 한 무리(인물 크기비 3, 아이콘 2 이내).
   인자: <src> <dst> <targets.json>   targets = [[슬라이드, "도형이름", 순번, "icon"|"illust"], ...]"""
import io, json, os, sys, time, statistics
from PIL import Image
from pptx import Presentation
sys.stdout.reconfigure(encoding="utf-8")
src, dst, tj = sys.argv[1:4]
T = json.load(open(tj, encoding="utf-8"))
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
p = Presentation(src)
def walk(sh):
    for s in sh:
        if s.shape_type == 6: yield from walk(s.shapes)
        else: yield s
tmp = dst + ".trim.pptx"
for sno, name, nth, kind in T:
    c = [s for s in walk(p.slides[sno - 1].shapes) if s.shape_type == 13 and s.name == name]
    if nth >= len(c): continue
    s = c[nth]
    im = Image.open(io.BytesIO(s.image.blob)).convert("RGBA"); w, h = im.size
    bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if not bb or (bb[2] - bb[0]) * (bb[3] - bb[1]) > 0.97 * w * h: continue
    L, Tp, W, H = s.left, s.top, s.width, s.height
    im = im.crop(bb); buf = io.BytesIO(); im.save(buf, "PNG"); buf.seek(0)
    _, rid = s.part.get_or_add_image_part(buf)
    bl = s._element.find(".//" + A + "blip"); bl.set(R + "embed", rid)
    ex = bl.find(A + "extLst")   # 예술 효과 원본 레이어가 있으면 저장 때 옛 그림으로 되돌아간다
    if ex is not None:
        for e in list(ex):
            if any(c.tag.endswith("}imgProps") for c in e): ex.remove(e)
    s.left, s.top = int(L + W * bb[0] / w), int(Tp + H * bb[1] / h)
    s.width, s.height = int(W * (bb[2] - bb[0]) / w), int(H * (bb[3] - bb[1]) / h)
p.save(tmp)

import win32com.client as win32
app = win32.Dispatch("PowerPoint.Application"); pres = app.Presentations.Open(os.path.abspath(tmp), WithWindow=False)
def sh_of(cc):
    o = []
    for i in range(1, cc.Count + 1):
        x = cc.Item(i); o += sh_of(x.GroupItems) if x.Type == 6 else [x]
    return o
try:
    by = {}
    for sno, name, nth, kind in T:
        alt = name.replace("그림 ", "Picture ")  # COM 은 한글 기본 이름을 영문으로 읽는다
        c = [x for x in sh_of(pres.Slides(sno).Shapes) if x.Name in (name, alt) and x.Type == 13]
        if nth < len(c): by.setdefault((sno, kind), []).append(c[nth])
    log = []
    for (sno, kind), items in by.items():
        # 같은 줄(가운데 y 가 가까움) 또는 같은 열(가운데 x 가 가까움)이면서 크기 비가 한도 안이면 한 무리
        lim = 3.0 if kind == "illust" else 2.0
        n = len(items); par = list(range(n))
        def fd(i):
            while par[i] != i: par[i] = par[par[i]]; i = par[i]
            return i
        M = [(x.Width * x.Height) ** .5 for x in items]
        C = [(x.Left + x.Width / 2, (x.Top + x.Height) if kind == "illust" else (x.Top + x.Height / 2)) for x in items]  # 인물은 발밑 줄
        for i in range(n):
            for j in range(i + 1, n):
                r = max(M[i], M[j]) / min(M[i], M[j]); tol = (0.5 if kind == "illust" else 0.35) * min(M[i], M[j])
                if r <= lim and (abs(C[i][1] - C[j][1]) < tol or abs(C[i][0] - C[j][0]) < tol):
                    par[fd(i)] = fd(j)
        gs = {}
        for i in range(n): gs.setdefault(fd(i), []).append(items[i])
        groups = list(gs.values())
        for g in groups:
            if len(g) < 2: continue
            tgt = statistics.median((x.Width * x.Height) ** .5 for x in g)
            for x in g:
                m = (x.Width * x.Height) ** .5; f = max(0.6, min(1.6, tgt / m))
                if abs(f - 1) < 0.04: continue
                cx, bot, cy = x.Left + x.Width / 2, x.Top + x.Height, x.Top + x.Height / 2
                x.LockAspectRatio = -1
                nw, nh = x.Width * f, x.Height * f
                x.Width = nw
                x.Left = cx - x.Width / 2
                x.Top = (bot - x.Height) if kind == "illust" else (cy - x.Height / 2)
                log.append((sno, x.Name, round(f, 2)))
    for l in log: print("  ", l)
    print("조정", len(log))
    pres.SaveAs(os.path.abspath(dst))
finally:
    pres.Close(); time.sleep(0.3)
os.remove(tmp)
