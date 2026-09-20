# -*- coding: utf-8 -*-
"""빌드용 원본 글꼴을 만든다 — 가끔만 돌리면 되는 스크립트.

Asta Sans (Google Fonts, OFL) 가변 글꼴에서 400/500/700 정적 인스턴스를 뽑고,
**한글 2,574자 + 라틴 + 사이트가 쓰는 기호**만 남겨 fonts/ 에 커밋해 둔다.
원본 가변 글꼴이 5.8MB 라 저장소에 그대로 둘 수 없기 때문이다.
평소 빌드(fonts.py)는 이 파일만 보면 되고 네트워크가 필요 없다.

쓰는 법
    py make-source-fonts.py        # 인터넷 필요. 결과: fonts/AstaSans-*.woff2

    글꼴을 바꾸거나 새 기호를 쓰고 싶을 때만 다시 돌린다.
"""
import io
import os
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fontTools import subset as ftsubset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'fonts')
TMP = os.path.join(OUT, '_full')

# 가변 글꼴 원본 + 남길 한글 목록을 가져올 곳
VAR_URL = 'https://raw.githubusercontent.com/google/fonts/main/ofl/astasans/AstaSans%5Bwght%5D.ttf'
KS_URL = ('https://cdn.jsdelivr.net/gh/spoqa/spoqa-han-sans@latest'
          '/Subset/SpoqaHanSansNeo/SpoqaHanSansNeo-Regular.woff2')

WEIGHTS = [400, 500, 700]

# 사이트가 쓰는 기호 — 빠지면 그 글자만 폴백 글꼴로 튄다
SYMBOLS = (
    ''.join(chr(c) for c in range(0x20, 0x7F))
    + '·…—–−‘’“”«»×÷±→←↑↓↔─│✓№™©®°'
    + '₩$€¥£‰①②③④⑤⑥⑦⑧⑨⑩'
)


def fetch(url, path):
    if os.path.exists(path):
        print('  있음: %s' % os.path.basename(path))
        return
    print('  내려받는 중: %s' % os.path.basename(path))
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=300) as r, open(path, 'wb') as f:
        f.write(r.read())


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)

    var_path = os.path.join(TMP, 'AstaSans-var.ttf')
    fetch(VAR_URL, var_path)

    # 남길 한글은 KS X 1001 2,574자 — Spoqa 배포 subset 의 cmap 을 목록으로만 빌려 쓴다.
    ks = os.path.join(TMP, 'ks-ref.woff2')
    fetch(KS_URL, ks)
    keep = {c for c in TTFont(ks).getBestCmap()}
    keep |= {ord(c) for c in SYMBOLS}

    have = set(TTFont(var_path).getBestCmap())
    miss = sorted(c for c in keep if c not in have)
    if miss:
        print('  원본에 없는 글자 %d개: %s' % (len(miss), ''.join(chr(c) for c in miss)))
    keep &= have
    print('남길 글자 %d자' % len(keep))

    for w in WEIGHTS:
        font = instancer.instantiateVariableFont(
            TTFont(var_path), {'wght': w}, updateFontNames=True, inplace=False)

        opt = ftsubset.Options()
        opt.layout_features = ['*']
        opt.notdef_outline = True
        sub = ftsubset.Subsetter(options=opt)
        sub.populate(unicodes=sorted(keep))
        sub.subset(font)
        font.flavor = 'woff2'

        dst = os.path.join(OUT, 'AstaSans-%d.woff2' % w)
        font.save(dst)
        print('  %s  %6.1f KB  (내부 이름: %s)'
              % (os.path.basename(dst), os.path.getsize(dst) / 1024,
                 font['name'].getDebugName(1)))

    print('\n완료. _full/ 은 임시 내려받기 폴더라 커밋하지 않는다.')


if __name__ == '__main__':
    main()
