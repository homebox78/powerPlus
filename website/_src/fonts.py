# -*- coding: utf-8 -*-
"""글꼴 서브셋 생성기 — 생성된 페이지에 실제로 쓰인 글자만 남긴다.

왜 필요한가
    서브셋을 손으로 만들어 두면 문구를 고칠 때마다 서브셋에 없는 글자가 생기고,
    그 글자만 조용히 폴백 글꼴(맑은 고딕)로 렌더된다. 눈에 잘 안 띄는데 줄 높이와
    자폭이 달라서 한 줄 안에서 글자가 튄다. 실제로 2026-09 까지 `—` `−` `✕`
    세 글자가 그 상태였다.
    그래서 빌드 마지막에 이 스크립트를 돌려 **그때 쓰인 글자로** 서브셋을 다시 만든다.

쓰는 법
    py fonts.py            # ../ 의 html 5장을 훑어 ../asta-{400,500,700}.woff2 생성

원본 글꼴
    fonts/AstaSans-{400,500,700}.woff2 (한글 2,574자)
    Asta Sans (Google Fonts, OFL). 저장소에 함께 두어 빌드에 네트워크가 필요 없다.
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fontTools.subset import Subsetter, Options
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
SRC = os.path.join(HERE, 'fonts')

PAGES = ['index.html', 'features.html', 'usecases.html', 'pricing.html', 'docs.html']
WEIGHTS = ['400', '500', '700']

# 스크립트가 나중에 만들어 넣는 글자까지 놓치지 않게 항상 넣어 둔다.
# 여기에 없는 기호를 본문에 쓰면 fonts.py 가 "원본에 없는 글자" 로 알려 준다.
ALWAYS = (
    ''.join(chr(c) for c in range(0x20, 0x7F))      # 기본 라틴 + 숫자 + 문장부호
    + '·…—–−‘’“”×→←↑↓₩°'                            # 사이트가 실제로 쓰는 기호
)


def used_chars():
    """페이지 파일을 통째로 훑는다.

    태그를 벗기지 않는 이유: 스크립트 안의 문자열이나 속성값으로 들어 있다가
    나중에 화면에 나오는 글자(예: 검색 결과 없음 안내)를 놓치지 않기 위해서다.
    라틴 몇 자를 더 넣는 대신 빠지는 일이 없다.
    """
    chars = set(ALWAYS)
    for p in PAGES:
        path = os.path.join(SITE, p)
        if not os.path.exists(path):
            print('  건너뜀(없음): %s' % p)
            continue
        chars |= set(open(path, encoding='utf-8').read())
    return {c for c in chars if c.strip() or c == ' '}


def build(chars):
    text = ''.join(sorted(chars))
    total = 0
    for weight in WEIGHTS:
        src = os.path.join(SRC, 'AstaSans-%s.woff2' % weight)
        if not os.path.exists(src):
            sys.exit('원본 글꼴이 없습니다: %s' % src)

        font = TTFont(src)
        have = set(font.getBestCmap())
        missing = sorted(c for c in chars if ord(c) not in have)
        if missing:
            # 원본에 없는 글자는 어차피 폴백이다. 조용히 넘기지 않고 알린다.
            print('  [%s] 원본에 없는 글자 %d개: %s' % (weight, len(missing), ''.join(missing)))

        opt = Options()
        opt.layout_features = ['*']
        opt.notdef_outline = True
        sub = Subsetter(options=opt)
        sub.populate(text=text)
        sub.subset(font)
        font.flavor = 'woff2'

        out = os.path.join(SITE, 'asta-%s.woff2' % weight)
        font.save(out)
        size = os.path.getsize(out)
        total += size
        print('  asta-%s.woff2  %6.1f KB' % (weight, size / 1024))
    return total


if __name__ == '__main__':
    chars = used_chars()
    hangul = sum(1 for c in chars if 0xAC00 <= ord(c) <= 0xD7A3)
    print('쓰인 글자 %d자 (한글 %d자)' % (len(chars), hangul))
    total = build(chars)
    print('합계 %.1f KB' % (total / 1024))
