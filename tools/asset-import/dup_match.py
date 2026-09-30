import json,os,sys
import numpy as np
from PIL import Image
S=sys.argv[1]
idx=json.load(open(S+"/idxmap.json",encoding="utf-8"))
old={int(k):v["path"] for k,v in idx.items() if 401<=int(k)<=566}
def feat(p):
    im=Image.open(p).convert("RGBA"); w,h=im.size
    bg=Image.new("RGBA",im.size,(128,128,128,255)); bg.alpha_composite(im)
    g=np.array(bg.convert("L").resize((32,32),Image.BILINEAR)).astype(float)
    g=(g-g.mean())/(g.std()+1e-6)
    return g.ravel(), w/h
O={k:feat(p) for k,p in old.items()}
res=[]
for fn in sorted(os.listdir(S+"/il/raw")):
    f,ar=feat(S+"/il/raw/"+fn)
    best=None
    for k,(g,oar) in O.items():
        if abs(np.log(ar/oar))>0.25: continue
        c=float((f*g).mean())
        if best is None or c>best[1]: best=(k,c)
    res.append((fn,best))
json.dump(res,open(S+"/il/match.json","w"))
hi=[r for r in res if r[1] and r[1][1]>0.6]
print(len(hi))
used={}
for fn,(k,c) in hi: used.setdefault(k,[]).append((fn,round(c,2)))
print(len(used)); 
for k in sorted(used): print(k,used[k])
