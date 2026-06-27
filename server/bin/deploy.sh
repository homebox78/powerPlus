#!/usr/bin/env bash
# powerPlus 통합 배포 스크립트 (한 번에: 애드인 빌드 → 서버 코드 + 애드인 dist 업로드)
#   - config/config.php 는 서버 값(실DB·메일·관리자) 보존 위해 업로드하지 않음
#   - SSH/SCP 22번 포트, google_key.pem 사용
# 사용:  cd server && bash bin/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/.."   # → server/

set -a; source config/deploy.env; set +a
: "${DEPLOY_HOST:?deploy.env 에 DEPLOY_HOST 필요}"
: "${DEPLOY_USER:?deploy.env 에 DEPLOY_USER 필요}"
: "${DEPLOY_REMOTE_PATH:?deploy.env 에 DEPLOY_REMOTE_PATH 필요}"

KEY_SRC="${DEPLOY_KEY:-google_key.pem}"
[ -f "$KEY_SRC" ] || { echo "키 파일 없음: $KEY_SRC"; exit 1; }
KEY="$(mktemp)"; cp "$KEY_SRC" "$KEY"; chmod 600 "$KEY"
trap 'rm -f "$KEY"' EXIT

SSHOPT="-i $KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=20"
R="$DEPLOY_USER@$DEPLOY_HOST"
RP="$DEPLOY_REMOTE_PATH"

echo "→ 애드인 빌드"
( cd ../addin && npm run build >/dev/null 2>&1 ) && echo "  빌드 완료" || echo "  (빌드 실패/건너뜀 — 기존 dist 사용)"

echo "→ 원격 폴더 준비"
ssh $SSHOPT -p 22 "$R" "mkdir -p '$RP/src' '$RP/admin' '$RP/lib/PHPMailer' '$RP/sql' '$RP/bin' '$RP/app/assets' '$RP/uploads' '$RP/config' '$RP/logs' && chmod 777 '$RP/uploads'"

echo "→ 서버 코드 업로드"
scp $SSHOPT -P 22 index.php .htaccess README.md "$R:$RP/"
scp $SSHOPT -P 22 src/*.php                      "$R:$RP/src/"
scp $SSHOPT -P 22 admin/index.html              "$R:$RP/admin/"
scp $SSHOPT -P 22 lib/PHPMailer/*.php           "$R:$RP/lib/PHPMailer/"
scp $SSHOPT -P 22 sql/*.sql                     "$R:$RP/sql/"
scp $SSHOPT -P 22 bin/*.php                      "$R:$RP/bin/"
[ -f uploads/.htaccess ] && scp $SSHOPT -P 22 uploads/.htaccess "$R:$RP/uploads/"

if [ -d ../addin/dist ]; then
  echo "→ 애드인(dist) 업로드 → app/"
  scp $SSHOPT -P 22 ../addin/dist/taskpane.html ../addin/dist/taskpane.js \
                    ../addin/dist/commands.html ../addin/dist/commands.js "$R:$RP/app/"
  scp $SSHOPT -P 22 ../addin/dist/assets/* "$R:$RP/app/assets/" 2>/dev/null || true
fi

echo "✓ 배포 완료 (config/config.php 는 서버 값 보존)"
