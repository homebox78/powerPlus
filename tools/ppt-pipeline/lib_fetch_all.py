import json, os, urllib.request, urllib.parse, concurrent.futures as cf, io, sys
from PIL import Image
sys.stdout.reconfigure(encoding="utf-8")
B="https://hom2box.com/powerPlus/api/public/assets"
out="libthumb"; os.makedirs(out,exist_ok=True)
items=[]
for cat in ("icon","illust"):
  page=1
  while True:
    d=json.load(urllib.request.urlopen(B+"?"+urllib.parse.urlencode({"category":cat,"limit":200,"page":page}),timeout=60))
    data=d.get("data",[]); items+=data
    if len(data)<200: break
    page+=1
print(len(items))
json.dump([{k:i.get(k) for k in ("id","thumb_url","image_url","tags_ko","width","height")} for i in items],open("lib_index.json","w",encoding="utf-8"),ensure_ascii=False)
def get(i):
  f=os.path.join(out,i["id"]+".png")
  if os.path.exists(f): return
  try:
    b=urllib.request.urlopen(i["thumb_url"],timeout=60).read()
    Image.open(io.BytesIO(b)).convert("RGBA").save(f)
  except Exception as e: print("x",i["id"],e)
with cf.ThreadPoolExecutor(16) as ex: list(ex.map(get,items))
print("done")
