# -*- coding: utf-8 -*-
"""위치 키로 넘침 측정. 인자: <pptx> <out.json>"""
import os,sys,json,time
import win32com.client as win32
src=os.path.abspath(sys.argv[1])
app=win32.Dispatch("PowerPoint.Application"); pres=app.Presentations.Open(src, WithWindow=False)
res={}
def scan(shapes, sn):
    for i in range(1, shapes.Count+1):
        sh=shapes.Item(i)
        try: t=sh.Type
        except Exception: continue
        if t==6:
            try: scan(sh.GroupItems, sn)
            except Exception: pass
            continue
        try:
            if not sh.HasTextFrame or not sh.TextFrame.HasText: continue
            tf=sh.TextFrame
            if tf.WordWrap==0: continue
            need=tf.TextRange.BoundHeight+tf.MarginTop+tf.MarginBottom
            k="%d|%s|%d|%d"%(sn,sh.Name,round(sh.Left),round(sh.Top))
            res[k]=round(need-sh.Height,2)
        except Exception: pass
for s in range(1,pres.Slides.Count+1): scan(pres.Slides(s).Shapes,s)
pres.Close(); time.sleep(0.2)
json.dump(res, open(sys.argv[2],"w",encoding="utf-8"))
print(len(res))
