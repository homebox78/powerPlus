#!/usr/bin/env bash
# powerPlus 서버 배포 스크립트
#   config/deploy.env 의 SSH 정보 + google_key.pem 으로 서버에 코드 파일을 업로드한다.
#   - config/config.php 는 서버 값(실DB·메일·관리자)을 보존하기 위해 업로드하지 않는다.
#   - SSH/SCP 는 22번 포트 사용 (deploy.env 의 FTP 포트와 무관).
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

echo "→ $R:$RP 로 배포"
ssh $SSHOPT -p 22 "$R" "mkdir -p '$RP/src' '$RP/admin' '$RP/lib/PHPMailer' '$RP/sql' '$RP/config' '$RP/logs'"

scp $SSHOPT -P 22 index.php .htaccess README.md "$R:$RP/"
scp $SSHOPT -P 22 src/*.php                      "$R:$RP/src/"
scp $SSHOPT -P 22 admin/index.html              "$R:$RP/admin/"
scp $SSHOPT -P 22 lib/PHPMailer/*.php           "$R:$RP/lib/PHPMailer/"
scp $SSHOPT -P 22 sql/*.sql                     "$R:$RP/sql/"

echo "✓ 배포 완료 (config/config.php 는 서버 값 보존)"
