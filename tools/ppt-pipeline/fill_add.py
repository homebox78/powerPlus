# -*- coding: utf-8 -*-
"""허전한 자리에 일러스트·아이콘 넣기 — 투명 여백을 잘라 넣고(잉크 기준 크기) 가운데·바닥 좌표로 둔다.
   인자: <src> <dst> <adds.json>   adds = [[슬라이드, "이미지경로", 가운데x_pt, 바닥y_pt, 높이_pt], ...]
   넣은 도형 이름은 ADD_<파일명>. 넣은 뒤 반드시 렌더로 머리 띠·화살표와 겹치는지 본다."""
import json, os, sys
from PIL import Image
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
A = json.load(open(sys.argv[3], encoding="utf-8"))
app = win32.Dispatch("PowerPoint.Application")
pr = app.Presentations.Open(src, ReadOnly=False, WithWindow=False)
for sn, p, cx, by, h in A:
    im = Image.open(p).convert("RGBA"); bb = im.getchannel("A").getbbox()
    cp = os.path.splitext(p)[0] + "_crop.png"; im.crop(bb).save(cp)
    w = h * (bb[2] - bb[0]) / (bb[3] - bb[1])
    sh = pr.Slides(sn).Shapes.AddPicture(cp, False, True, cx - w / 2, by - h, w, h)
    sh.Name = "ADD_" + os.path.basename(os.path.splitext(p)[0])
    print(sn, sh.Name, round(w), h)
pr.SaveCopyAs(dst); pr.Close()
