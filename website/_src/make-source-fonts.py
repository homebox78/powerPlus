# -*- coding: utf-8 -*-
"""빌드용 원본 글꼴을 만든다 — 가끔만 돌리면 되는 스크립트.

왜 이런 단계가 있나
    Spoqa 가 배포하는 가벼운 Subset 판에는 `—`(em dash) 같은 기호가 빠져 있다.
    그 글자만 폴백 글꼴로 렌더돼서 한 줄 안에서 글자가 튄다.
    전체 글꼴(OTF)에는 들어 있지만 한 굵기에 12.6MB 라 저장소에 둘 수 없다.

    그래서 전체 글꼴에서 **한글 2,574자 + 라틴 + 사이트가 쓰는 기호**만 남긴
    원본을 한 번 만들어 fonts/ 에 커밋해 둔다. 평소 빌드(fonts.py)는 이 파일만
    보면 되고 네트워크가 필요 없다.

쓰는 법
    py make-source-fonts.py        # 인터넷 필요. 결과: fonts/SpoqaHanSansNeo-*.woff2

    글꼴을 바꾸거나 새 기호를 쓰고 싶을 때만 다시 돌린다.
"""
import io
import os
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fontTools.subset import Subsetter, Options
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'fonts')
CDN = 'https://cdn.jsdelivr.net/gh/spoqa/spoqa-han-sans@latest'
WEIGHTS = ['Regular', 'Medium', 'Bold']

# 사이트가 쓰는 기호 — 빠지면 그 글자만 폴백 글꼴로 튄다
SYMBOLS = (
    ''.join(chr(c) for c in range(0x20, 0x7F))
    + '·…—–−‘’“”«»×÷±→←↑↓↔─│┌┐└┘✓№™©®°㎡㎞㎏％±≤≥≠∙•◦▪▲▼◀▶★☆♥'
    + '₩$€¥£‰㈜㈎①②③④⑤⑥⑦⑧⑨⑩'
)


def fetch(url, path):
    if os.path.exists(path):
        print('  있음: %s' % os.path.basename(path))
        return
    print('  내려받는 중: %s' % os.path.basename(path))
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=180) as r, open(path, 'wb') as f:
        f.write(r.read())


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, '_full')
    os.makedirs(tmp, exist_ok=True)

    # 남길 한글 목록은 Spoqa 가 정한 Subset 판(KS X 1001, 2,574자)을 그대로 따른다.
    ref = os.path.join(tmp, 'ref-Regular.woff2')
    fetch('%s/Subset/SpoqaHanSansNeo/SpoqaHanSansNeo-Regular.woff2' % CDN, ref)
    keep = {c for c in TTFont(ref).getBestCmap()}
    keep |= {ord(c) for c in SYMBOLS}
    print('남길 글자 %d자' % len(keep))

    for w in WEIGHTS:
        otf = os.path.join(tmp, 'full-%s.otf' % w)
        fetch('%s/Original/SpoqaHanSansNeo/SpoqaHanSansNeo-%s.otf' % (CDN, w), otf)

        font = TTFont(otf)
        have = set(font.getBestCmap())
        miss = sorted(c for c in keep if c not in have)
        if miss:
            print('  [%s] 전체 글꼴에도 없는 글자 %d개: %s'
                  % (w, len(miss), ''.join(chr(c) for c in miss)))

        opt = Options()
        opt.layout_features = ['*']
        opt.notdef_outline = True
        sub = Subsetter(options=opt)
        sub.populate(unicodes=sorted(keep & have))
        sub.subset(font)
        font.flavor = 'woff2'

        dst = os.path.join(OUT, 'SpoqaHanSansNeo-%s.woff2' % w)
        font.save(dst)
        print('  %s  %.1f KB' % (os.path.basename(dst), os.path.getsize(dst) / 1024))

    print('\n완료. _full/ 은 임시 내려받기 폴더라 커밋하지 않는다.')


if __name__ == '__main__':
    main()
