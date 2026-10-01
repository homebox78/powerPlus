import json,os,urllib.request,io,sys
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
idx={i['id']:i for i in json.load(open('lib_index.json',encoding='utf-8'))}
os.makedirs('orig',exist_ok=True)
for x in sys.argv[1:]:
  f='orig/%s.png'%x
  b=urllib.request.urlopen(idx[x]['image_url'],timeout=60).read()
  im=Image.open(io.BytesIO(b)).convert('RGBA')
  bb=im.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox()
  if bb: im=im.crop(bb)
  im.save(f); print(x,im.size)
