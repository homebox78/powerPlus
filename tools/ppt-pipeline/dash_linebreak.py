# -*- coding: utf-8 -*-
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
IN = 72.0; VT = chr(11); SP = set(" \t\r\n" + VT + chr(13))
app = win32.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(src, WithWindow=False)
def sh_of(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i); o += sh_of(s.GroupItems) if s.Type == 6 else [s]
    return o
def nobreak(tr):
    n = 0
    for _ in range(4):
        txt = tr.Text; cnt = tr.Lines().Count; done = True
        for i in range(1, cnt):
            a = tr.Lines(i, 1); b = tr.Lines(i + 1, 1)
            e = a.Start + a.Length - 1; s = b.Start
            if e < 1 or s > len(txt): continue
            c1, c2 = txt[e - 1], txt[s - 1]
            if c1 in SP or c2 in SP: continue
            p = e
            while p > 1 and txt[p - 2] not in SP: p -= 1
            if p <= a.Start: continue
            tr.Characters(p, 0).InsertBefore(VT); n += 1; done = False; break
        if done: break
    return n
dashed = []
try:
    for sno in range(1, pres.Slides.Count + 1):
        for sh in sh_of(pres.Slides(sno).Shapes):
            if not sh.HasTextFrame: continue
            tf = sh.TextFrame; tr = tf.TextRange; t = tr.Text
            if not t.strip(): continue
            # ① 대시(—)가 든 "문단"이 2줄 이상으로 접히면 대시 뒤에서 줄을 나눈다(제목처럼 문단이 여럿인 건 제외)
            if "—" in t:
                for pi in range(1, tr.Paragraphs().Count + 1):
                    pr = tr.Paragraphs(pi); pt = pr.Text
                    if "—" not in pt or pr.Lines().Count < 2: continue
                    # 이전 어절 보정(VT) 제거 후 대시 기준으로 다시
                    while VT in pr.Text:
                        pr.Characters(pr.Text.index(VT) + 1, 1).Delete()
                    pt = pr.Text; pos = pt.find("—")
                    if pos + 1 < len(pt) and pt[pos + 1] == " ":
                        pr.Characters(pos + 2, 1).Delete()
                    pr.Characters(pos + 2, 0).InsertBefore(VT)
                    dashed.append((sno, pt.replace(chr(13), " ")[:44]))
                nobreak(tr)
            # ② s9 행 제목: 어절 보정 + 높이 맞춤
            if sno == 9 and sh.Left/IN < 0.6 and sh.Width/IN > 1.9 and sh.Height/IN > 1.0:
                for size in (tr.Font.Size, 8.5, 8.0, 7.5):
                    tr.Font.Size = size; k = nobreak(tr)
                    fit = tr.BoundHeight <= sh.Height - tf.MarginTop - tf.MarginBottom
                    print(f"s9 행제목 '{t.split(chr(13))[0][:12]}' {size}pt 어절{k} 높이 {tr.BoundHeight/IN:.2f}/{sh.Height/IN:.2f} {'OK' if fit else '넘침'}")
                    if fit: break
            # ③ s15 KPI 카드: 큰제목(15pt, h≈0.36) 아래 여백 0, 설명(7.6pt) 위로 당김
            if sno == 15:
                fs = tr.Font.Size
                if abs(sh.Height/IN - 0.36) < 0.03 and fs >= 14:
                    tf.MarginBottom = 0
                elif abs(sh.Height/IN - 0.40) < 0.03 and fs < 9 and abs(sh.Top/IN - 2.68) < 0.05:
                    tf.MarginTop = 0; sh.Top -= 0.07 * IN
                    print(f"s15 설명 위로: '{t[:14]}' top {sh.Top/IN:.2f}")
    print("대시 줄바꿈:", len(dashed))
    for d in dashed: print("  ", d)
    pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
