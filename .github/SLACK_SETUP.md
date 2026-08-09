# Slack 자동 진행보고 설정 (1회만)

main 브랜치에 푸시하면 `#21-개발하는디자이너` 채널에 커밋 요약이 주간보고 형식으로 자동 전송됩니다.
동작하려면 **웹훅 URL 1개**만 등록하면 됩니다.

## 1. Slack 웹훅 만들기 (soli-hack 워크스페이스)

1. https://api.slack.com/apps → **Create New App** → *From scratch*
2. 이름 `powerPlus 보고봇`, 워크스페이스 **Soli-Hack** 선택
3. 좌측 **Incoming Webhooks** → 토글 **On** → **Add New Webhook to Workspace**
4. 채널 `#21-개발하는디자이너` 선택 → 허용
5. 생성된 `https://hooks.slack.com/services/...` URL 복사

> 워크스페이스가 앱 설치를 제한하면 관리자 승인 요청이 뜹니다 — 운영진(C.J. Lee)에게 승인 요청.

## 2. GitHub Secret 등록

1. https://github.com/homebox78/powerPlus/settings/secrets/actions
2. **New repository secret** → 이름 `SLACK_WEBHOOK_URL`, 값 = 복사한 웹훅 URL

## 끝. 이후 동작

- main 푸시마다: `📌 진행 업데이트 — 날짜 / 한 일(커밋 불릿) / 변경 내역 링크` 자동 전송
- 알리고 싶지 않은 커밋: 메시지에 `[skip-slack]` 포함
- 시크릿을 안 넣으면 아무 일도 안 함(빌드 실패 없음)

⚠️ 웹훅 URL은 비밀값입니다 — 공개 repo 소스·채팅에 붙여넣지 말 것 (Secrets에만).
