"""알파만으로 자른다 — 픽셀 색·알파는 절대 바꾸지 않는다(사용자가 투명 처리함).
행 → 행 안의 열 투영으로 칸을 나누고, 작은 조각은 가까운 큰 조각에 합친다."""
import os,sys,json
import numpy as np
from PIL import Image
D="D:/powerPlus/data/_stage/illust"; OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)
def runs(v,gap,minlen):
    idx=np.where(v)[0]
    if not len(idx): return []
    rs=[];s=p=idx[0]
    for i in idx[1:]:
        if i-p>gap: rs.append([s,p]); s=i
        p=i
    rs.append([s,p]); return [r for r in rs if r[1]-r[0]>=minlen]
rep={}
for si,fn in enumerate(sorted(os.listdir(D)),1):
    im=Image.open(f"{D}/{fn}").convert("RGBA"); a=np.array(im); A=a[...,3]; m=A>24
    H,W=m.shape
    rows=runs(m.sum(1)>2,int(H*0.018),int(H*0.03))
    boxes=[]
    for y0,y1 in rows:
        band=m[y0:y1+1]
        cols=runs(band.sum(0)>1,int(W*0.014),4)
        for x0,x1 in cols:
            sub=band[:,x0:x1+1]; ys=np.where(sub.any(1))[0]
            boxes.append([x0,y0+ys[0],x1,y0+ys[-1],int(sub.sum())])
    # 작은 조각(최대의 12% 미만 잉크) → 같은 행의 가장 가까운 큰 조각에 합침
    if boxes:
        big=max(b[4] for b in boxes); keep=[b for b in boxes if b[4]>=big*0.12]; small=[b for b in boxes if b[4]<big*0.12]
        for s in small:
            cx,cy=(s[0]+s[2])/2,(s[1]+s[3])/2
            t=min(keep,key=lambda k:max(0,k[0]-cx,cx-k[2])+max(0,k[1]-cy,cy-k[3]))
            t[0]=min(t[0],s[0]);t[1]=min(t[1],s[1]);t[2]=max(t[2],s[2]);t[3]=max(t[3],s[3]);t[4]+=s[4]
        boxes=keep

    # 넓은 조각(여러 장면이 붙음) → 안쪽 빈 세로줄로 다시 나눈다
    ws=sorted(b[2]-b[0] for b in boxes); med=ws[len(ws)//2] if ws else 1
    out=[]; forced=[]
    for b in boxes:
        x0,y0,x1,y1,n=b
        if x1-x0<=1.55*med: out.append(b); continue
        sub=m[y0:y1+1,x0:x1+1]; col=sub.sum(0)
        z=np.where(col==0)[0]
        gaps=[]
        if len(z):
            s=p=z[0]
            for i in z[1:]:
                if i-p>1: gaps.append((s,p)); s=i
                p=i
            gaps.append((s,p))
        cuts=[(g[0]+g[1])//2 for g in gaps if g[0]>0 and g[1]<len(col)-1]
        segs=[];last=0
        for c in cuts:
            if c-last>=0.35*med and (len(col)-c)>=0.35*med: segs.append((last,c)); last=c
        segs.append((last,len(col)-1))
        if len(segs)==1:
            k=int(len(col)*0.3)+int(np.argmin(col[int(len(col)*0.3):int(len(col)*0.7)]))
            segs=[(0,k),(k,len(col)-1)]; forced.append(fn)
        for a0,a1 in segs:
            s2=sub[:,a0:a1+1]
            if s2.sum()==0: continue
            ys=np.where(s2.any(1))[0]; xs=np.where(s2.any(0))[0]
            out.append([x0+a0+xs[0],y0+ys[0],x0+a0+xs[-1],y0+ys[-1],int(s2.sum())])
    boxes=out
    if forced: print("강제분할",si,forced)
    boxes.sort(key=lambda b:(round(b[1]/(H*0.25)),b[0]))
    names=[]
    for k,(x0,y0,x1,y1,_) in enumerate(boxes,1):
        pad=4
        c=im.crop((max(0,x0-pad),max(0,y0-pad),min(W,x1+pad+1),min(H,y1+pad+1)))
        # 크롭 안에 다른 칸의 픽셀이 들어오지 않았는지: 크롭은 x·y 범위가 칸 전용이므로 그대로 둔다
        nm=f"s{si:02d}_{k:02d}.png"; c.save(f"{OUT}/{nm}"); names.append([nm,c.size])
    rep[si]=[fn,len(boxes)]
json.dump(rep,open(OUT+"/../cutrep.json","w"),ensure_ascii=False)
for k,v in rep.items(): print(k,v[1],end=" | ")
