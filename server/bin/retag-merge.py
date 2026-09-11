# -*- coding: utf-8 -*-
import json, os, re, glob, unicodedata, html
BASE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.join(BASE, '..', '..', 'tasks')
idxmap = json.load(open(os.path.join(BASE, 'idxmap.json'), encoding='utf-8'))
items = {}
srcs = glob.glob(os.path.join(BASE, 'res_*.json'))
for p in srcs:
    s = open(p, encoding='utf-8', errors='replace').read()
    a = s.find('[{"idx"'); b = s.rfind(']')
    if a < 0: continue
    try:
        arr = json.loads(s[a:b+1])
    except Exception as e:
        print('PARSE FAIL', os.path.basename(p), e); continue
    for it in arr:
        items[int(it['idx'])] = it
def dd(xs):
    out=[]; seen=set()
    for x in xs:
        x = html.unescape(unicodedata.normalize('NFC', str(x).strip()))
        k = x.lower()
        if k and k not in seen: seen.add(k); out.append(x)
    return out
out = {}
short = []
for idx_s, aid in idxmap.items():
    idx = int(idx_s)
    it = items.get(idx)
    if not it: continue
    ko = dd(it.get('ko', [])); en = dd(it.get('en', []))
    if len(ko) < 12 or len(en) < 10: short.append((idx, aid, len(ko), len(en)))
    out[aid] = {'ko': ko, 'en': en}
missing = [int(k) for k in idxmap if int(k) not in items]
json.dump(out, open(os.path.join(BASE, '_retag.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('total idx', len(idxmap), 'tagged', len(out), 'missing', missing, 'short', short)
