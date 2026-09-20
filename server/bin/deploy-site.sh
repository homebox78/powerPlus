#!/usr/bin/env bash
# 소개 사이트(website/)만 배포한다.  →  https://hom2box.com/powerPlus/site/
#
# deploy.sh 는 애드인을 다시 빌드하고 서버 코드까지 통째로 올린다.
# 사이트 문구 한 줄 고치자고 그걸 돌리면 애드인 번들이 같이 덮이고,
# 두 PC 에서 각자 배포하면 최신 번들이 옛것에 덮이는 사고가 난다(2026-06-30).
# 사이트만 바꿨을 때는 이 스크립트를 쓴다.
#
# 사용:  cd server && bash bin/deploy-site.sh
set -euo pipefail
cd "$(dirname "$0")/.."   # → server/

set -a; source config/deploy.env; set +a
: "${DEPLOY_HOST:?deploy.env 에 DEPLOY_HOST 필요}"
: "${DEPLOY_USER:?deploy.env 에 DEPLOY_USER 필요}"
: "${DEPLOY_REMOTE_PATH:?deploy.env 에 DEPLOY_REMOTE_PATH 필요}"

[ -d ../website ] || { echo "website/ 가 없습니다"; exit 1; }

KEY_SRC="${DEPLOY_KEY:-google_key.pem}"
[ -f "$KEY_SRC" ] || { echo "키 파일 없음: $KEY_SRC"; exit 1; }
KEY="$(mktemp)"; cp "$KEY_SRC" "$KEY"; chmod 600 "$KEY"
trap 'rm -f "$KEY"' EXIT

KNOWN="config/known_hosts"
if [ ! -s "$KNOWN" ]; then
  echo "→ known_hosts 최초 등록: $DEPLOY_HOST"
  ssh-keyscan -p 22 "$DEPLOY_HOST" > "$KNOWN" 2>/dev/null
  [ -s "$KNOWN" ] || { echo "ssh-keyscan 실패: $DEPLOY_HOST"; exit 1; }
fi
SSHOPT="-i $KEY -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$KNOWN -o ConnectTimeout=20"
R="$DEPLOY_USER@$DEPLOY_HOST"
RP="$DEPLOY_REMOTE_PATH"

# 생성물이 최신인지 먼저 본다 — build.py 만 고치고 publish.py 를 안 돌리면
# 사이트는 그대로인 채 배포만 성공한다.
if [ ../website/_src/build.py -nt ../website/index.html ]; then
  echo "!! _src/build.py 가 index.html 보다 새롭습니다."
  echo "   cd website/_src && py build.py && py polish.py index.html features.html usecases.html pricing.html && py publish.py && py fonts.py"
  exit 1
fi

echo "→ 소개 사이트 → $RP/site"
( cd ../website && tar -cf - *.html img shots *.woff2 ) \
  | ssh $SSHOPT -p 22 "$R" "mkdir -p '$RP/site' && tar -xf - -C '$RP/site'"

echo "→ 확인"
for p in "" features.html usecases.html pricing.html docs.html; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://$DEPLOY_HOST/powerPlus/site/$p")
  echo "   /site/$p  $code"
done
echo "완료 — https://$DEPLOY_HOST/powerPlus/site/"
