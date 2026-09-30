import json,os,sys,collections
import numpy as np
from PIL import Image
S=sys.argv[1]
idx=json.load(open(S+"/idxmap.json",encoding="utf-8"))
def feat(p):
    im=Image.open(p).convert("RGBA")
    bg=Image.new("RGBA",im.size,(128,128,128,255)); bg.alpha_composite(im)
    g=np.array(bg.convert("L").resize((32,32))).astype(float); return ((g-g.mean())/(g.std()+1e-6)).ravel()
res=json.load(open(S+"/il/match.json"))
dup={}
for sh in ["s03","s04","s05","s06","s07","s73","s74"]:
    new=sorted(f for f in os.listdir(S+"/il/raw") if f.startswith(sh))
    keys=collections.Counter(b[0] for fn,b in res if fn.startswith(sh) and b and b[1]>=0.85)
    # 그 시트가 가리키는 옛 시트(같은 원본 stem)의 조각 전부
    stems=collections.Counter(os.path.basename(idx[str(k)]["path"])[:13] for k in keys)
    stem=stems.most_common(1)[0][0]
    olds=[int(k) for k,v in idx.items() if 401<=int(k)<=566 and os.path.basename(v["path"]).startswith(stem)]
    F={f:feat(S+"/il/raw/"+f) for f in new}; O={k:feat(idx[str(k)]["path"]) for k in olds}
    pairs=sorted(((float((F[f]*O[k]).mean()),f,k) for f in new for k in olds),reverse=True)
    uf,uk=set(),set()
    for c,f,k in pairs:
        if f in uf or k in uk: continue
        dup[f]=[k,round(c,2)]; uf.add(f); uk.add(k)
    print(sh,stem,len(new),len(olds),"매칭",sum(1 for f in new if f in dup),"최저",min(dup[f][1] for f in new if f in dup))
json.dump(dup,open(S+"/il/dup.json","w"))
