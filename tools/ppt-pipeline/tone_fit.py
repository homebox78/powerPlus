# -*- coding: utf-8 -*-
"""fixlist 대상 도형의 글자를 0.25pt 씩 줄여 넘침 흡수. 인자: <src> <dst> <fixlist.json>
최대 2.0pt 까지, 그래도 안 들어가면 원래 크기로 되돌리고 보고."""
import os,sys,json,io,time
import win32com.client as win32
src=os.path.abspath(sys.argv[1]); dst=os.path.abspath(sys.argv[2])
fix=json.load(open(sys.argv[3],encoding="utf-8"))
app=win32.Dispatch("PowerPoint.Application"); pres=app.Presentations.Open(src, WithWindow=False)
done=[]; fail=[]
def over(sh):
    tf=sh.TextFrame
    return tf.TextRange.BoundHeight+tf.MarginTop+tf.MarginBottom-sh.Height
def scan(shapes, sn):
    for i in range(1, shapes.Count+1):
        sh=shapes.Item(i)
        try: t=sh.Type
        except Exception: continue
        if t==6:
            try: scan(sh.GroupItems, sn)
            except Exception: pass
            continue
        k="%d|%s|%d|%d"%(sn,sh.Name,round(sh.Left),round(sh.Top))
        if k not in fix: continue
        try:
            tr=sh.TextFrame.TextRange
            orig=[tr.Characters(j+1,1).Font.Size for j in range(tr.Length)]
            cut=0.0
            while cut < 2.0 and over(sh) > 1.0:
                cut += 0.25
                for j in range(tr.Length):
                    tr.Characters(j+1,1).Font.Size = max(5.0, orig[j]-cut)
            if over(sh) > 1.0:
                for j in range(tr.Length): tr.Characters(j+1,1).Font.Size = orig[j]
                fail.append((k, round(over(sh),1)))
            else:
                done.append((k, cut, round(over(sh),1)))
        except Exception as e:
            fail.append((k, str(e)[:40]))
for s in range(1,pres.Slides.Count+1): scan(pres.Slides(s).Shapes,s)
pres.SaveAs(dst); pres.Close(); time.sleep(0.3)
o=io.open("fit_log.txt","w",encoding="utf-8")
o.write("흡수 %d / 실패 %d\n\n"%(len(done),len(fail)))
for k,c,r in done: o.write("OK   %-44s -%.2fpt (잔여 %.1f)\n"%(k,c,r))
for k,r in fail: o.write("FAIL %-44s %s\n"%(k,r))
o.close(); print("ok",len(done),"fail",len(fail))
