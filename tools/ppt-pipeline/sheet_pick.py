"""렌더 폴더 → 번호 컨택트시트(3열, 장 번호 목록). 인자: <폴더> <출력> 번호..."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
d, out = sys.argv[1:3]
nos = [int(x) for x in sys.argv[3:]]
C, CW = 3, 900
CH = int(CW * 7.5 / 10.8333)
R = (len(nos) + C - 1) // C
sh = Image.new("RGB", (C * CW, R * CH), (200, 205, 215))
dr = ImageDraw.Draw(sh)
fb = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 30)
for i, n in enumerate(nos):
    im = Image.open(os.path.join(d, "s%02d.png" % n)).convert("RGB").resize((CW - 6, CH - 6), Image.LANCZOS)
    x, y = (i % C) * CW, (i // C) * CH
    sh.paste(im, (x + 3, y + 3))
    dr.rectangle([x + 6, y + 6, x + 60, y + 44], fill=(214, 40, 40))
    dr.text((x + 12, y + 8), str(n), fill="white", font=fb)
sh.save(out)
