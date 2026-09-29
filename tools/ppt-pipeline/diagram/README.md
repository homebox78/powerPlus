# 이미지 도식 → 도형·표 재제작

`diag.py` 의 `Diagram(slide, pic, 원본px폭, 원본px높이)` 가 원본 그림 좌표(px)를 슬라이드 좌표로 옮긴다.
원본 그림을 옆에 띄워 두고 px 좌표 그대로 `box`·`label`·`line`·`table` 을 적으면 같은 자리에 도형이 생긴다.
`finish()` 가 새 도형을 원래 그림의 z-순서 자리로 옮기고 그림을 지운다.

    python run_diag.py <src.pptx> <dst.pptx> d_s20 d_s21 ...

- `d_s*.py` 는 청주시 제안요약서 v0.3 에서 쓴 실제 명세(작업 예시). 아이콘 경로 `assets/icon_*.png` 는
  powerPlus 공개 API 에서 받은 파일이다(`?ids=icon_1397`).
- 규칙: 기본 7pt · 마름모·셰브런은 도형 안 글상자가 좁아 접히므로 **위에 글상자를 따로 얹는다**(`diamond`, `label`)
- ⚠️ 문자열에 줄바꿈(`\n`)이 든 명세는 셸 heredoc 치환으로 고치지 말 것 — 실제 줄바꿈이 박혀 파일이 깨진다.
