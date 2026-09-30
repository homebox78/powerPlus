"""파워플러스 공개 API 로 아이콘 후보 검색 → 번호 시트. 인자: <출력폴더> 검색어1 검색어2 ... (카테고리 icon)"""
import io, json, os, sys, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding="utf-8")
out = sys.argv[1]; qs = sys.argv[2:]
os.makedirs(out, exist_ok=True)
font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 16)
BASE = "https://hom2box.com/powerPlus/api/public/assets"
cat = os.environ.get("CAT", "icon")
for q in qs:
    url = BASE + "?" + urllib.parse.urlencode({"q": q, "category": cat, "limit": 24})
    d = json.load(urllib.request.urlopen(url, timeout=30))
    items = d.get("data", [])
    cells = []
    for it in items:
        try:
            b = urllib.request.urlopen(it["thumb_url"], timeout=30).read()
            im = Image.open(io.BytesIO(b)).convert("RGBA")
        except Exception:
            continue
        cells.append((it["id"], im))
    S = Image.new("RGB", (6 * 170, ((len(cells) + 5) // 6) * 190 or 190), "white")
    dr = ImageDraw.Draw(S)
    for k, (i, im) in enumerate(cells):
        im.thumbnail((150, 150))
        x, y = (k % 6) * 170 + 10, (k // 6) * 190 + 5
        S.paste(im, (x, y), im)
        dr.text((x, y + 155), i, fill="black", font=font)
    S.save(os.path.join(out, "q_%s.png" % q.replace(" ", "_")))
    print(q, len(cells), [i for i, _ in cells])
