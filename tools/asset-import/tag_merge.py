import json, glob, unicodedata, sys, os
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
idx = json.load(open(S + "/tagidx.json", encoding="utf-8"))
STY = {
 "g1": (["3D 인물", "얼굴없는", "비즈니스", "진지한"], ["3d", "faceless", "business", "serious"]),
 "g2": (["3D 캐릭터", "친근한", "설명"], ["3d character", "friendly", "explaining"]),
 "g3": (["3D 캐릭터", "정면", "담당자 소개", "신뢰"], ["3d character", "front view", "staff profile", "trust"]),
 "g4": (["평면 일러스트", "남색", "관제", "진지한", "무게감"], ["flat illustration", "navy", "control", "serious", "weighty"]),
 "g5": (["평면 일러스트", "업무 장면", "차분한"], ["flat illustration", "work scene", "calm"]),
 "g6": (["평면 일러스트", "경쾌한", "가벼운", "밝은"], ["flat illustration", "cheerful", "light", "bright"]),
 "g7": (["평면 일러스트", "전신 인물", "소개"], ["flat illustration", "full body", "introduction"]),
}
got = {}
for f in sorted(glob.glob(S + "/tags_out/a*.json")):
    for r in json.load(open(f, encoding="utf-8")):
        got[int(r["idx"])] = r
miss = [n for n in range(1, len(idx) + 1) if n not in got]
print("받음", len(got), "빠짐", miss[:40], len(miss))
def clean(lst, pre, cap):
    out, seen = [], set()
    for w in pre + lst:
        w = unicodedata.normalize("NFC", str(w)).strip()
        k = w.lower()
        if not w or k in seen or len(w) > 30:
            continue
        seen.add(k); out.append(w)
    return out[:cap]
tags = {}
short = []
for n, fn in idx.items():
    r = got.get(int(n))
    if not r:
        continue
    g = fn.split("_")[0]
    ko = clean(r["ko"], STY[g][0], 26)
    en = clean(r["en"], STY[g][1], 26)
    if len(ko) < 18 or len(en) < 18:
        short.append((n, len(ko), len(en)))
    tags["illust/" + fn] = {"ko": ko, "en": en}
print("태그", len(tags), "짧음", short)
json.dump(tags, open(S + "/tags.json", "w", encoding="utf-8"), ensure_ascii=False)
