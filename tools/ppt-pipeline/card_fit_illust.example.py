# -*- coding: utf-8 -*-
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); IN = 72.0; PAD = 0.16 * IN; GAP = 0.16 * IN
app = win32.Dispatch("PowerPoint.Application"); pres = app.Presentations.Open(src, WithWindow=False)
try:
    sl = pres.Slides(12); S = {s.Id: s for s in sl.Shapes}
    def fit(card, title, body, icon):
        tb = body.TextFrame.TextRange; bot = tb.BoundTop + tb.BoundHeight
        card.Height = bot - card.Top + PAD
        icon.Top = card.Top + card.Height / 2 - icon.Height / 2
    c1, c2 = S[58], S[66]
    fit(c1, S[64], S[65], S[95])
    d = (c1.Top + c1.Height + GAP) - c2.Top
    for i in (66, 70, 71, 96): S[i].Top += d
    fit(c2, S[70], S[71], S[96])
    top = c2.Top + c2.Height + 0.22 * IN; bot = 6.17 * IN - 0.18 * IN
    from PIL import Image
    im = Image.open(os.path.abspath("il305.png")); r = im.width / im.height
    h = bot - top; w = h * r
    if w > c1.Width: w = c1.Width; h = w / r
    pic = sl.Shapes.AddPicture(os.path.abspath("il305.png"), 0, -1, c1.Left + (c1.Width - w) / 2, top + (bot - top - h) / 2, w, h)
    pic.Name = "PPILLUST"
    print(f"card1 {c1.Top/IN:.2f}~{(c1.Top+c1.Height)/IN:.2f}  card2 {c2.Top/IN:.2f}~{(c2.Top+c2.Height)/IN:.2f}  일러 {pic.Top/IN:.2f} {pic.Width/IN:.2f}x{pic.Height/IN:.2f}")
    pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
