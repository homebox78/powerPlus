# -*- coding: utf-8 -*-
"""powerPlus 에서 검색어별 후보 아이콘을 받아 시트로 만든다.
사용: python find.py <outdir> "번호:검색어" ...
"""
import json, os, sys, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont
import io

out = os.path.abspath(sys.argv[1])
os.makedirs(out, exist_ok=True)
API = "https://hom2box.com/powerPlus/api/public/assets"
get = lambda u: urllib.request.urlopen(u, timeout=25).read()

rows = []
for arg in sys.argv[2:]:
    no, q = arg.split(":", 1)
    u = API + "?" + urllib.parse.urlencode({"q": q, "category": "icon", "limit": 5})
    d = json.loads(get(u).decode())
    got = []
    for a in d["data"]:
        try:
            blob = get(a["thumb_url"] or a["image_url"])
            got.append((a["id"], a.get("style_sig"), (a.get("tags") or [""])[0], blob))
        except Exception:
            pass
    rows.append((no, q, d.get("total", 0), got))

CELL = 190
W = CELL * 5 + 240
H = sum(CELL + 34 for _ in rows)
sh = Image.new("RGB", (W, H), (236, 239, 245))
dr = ImageDraw.Draw(sh)
try:
    fb = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 17)
    fn = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 12)
except Exception:
    fb = fn = ImageFont.load_default()

y = 0
for no, q, total, got in rows:
    dr.text((10, y + CELL // 2 - 20), f"{no}번", fill=(214, 40, 40), font=fb)
    dr.text((10, y + CELL // 2 + 2), f"'{q}'", fill=(40, 40, 40), font=fn)
    dr.text((10, y + CELL // 2 + 20), f"{total}건", fill=(120, 124, 136), font=fn)
    for i, (aid, sig, tag, blob) in enumerate(got):
        im = Image.open(io.BytesIO(blob)).convert("RGBA")
        im.thumbnail((CELL - 34, CELL - 34), Image.LANCZOS)
        bg = Image.new("RGBA", (CELL, CELL), (255, 255, 255, 255))
        bg.paste(im, ((CELL - im.width) // 2, (CELL - im.height) // 2), im)
        x = 240 + i * CELL
        sh.paste(bg, (x, y), bg)
        dr.rectangle([x + 3, y + 3, x + 26, y + 24], fill=(40, 44, 56))
        dr.text((x + 10, y + 4), chr(97 + i), fill=(255, 255, 255), font=fb)
        dr.text((x + 4, y + CELL + 3), f"{aid} · {sig or '-'}", fill=(60, 60, 60), font=fn)
        dr.text((x + 4, y + CELL + 18), tag[:14], fill=(110, 114, 126), font=fn)
        open(os.path.join(out, f"{no}_{chr(97+i)}_{aid}.png"), "wb").write(blob)
    y += CELL + 34

p = os.path.join(out, "candidates.png")
sh.save(p)
sys.stdout.reconfigure(encoding="utf-8")
print(p)
