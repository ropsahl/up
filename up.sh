#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo Router in: $DIR
echo Services in $1
PORT=$2
ENV=$3
CMDLINE=" -u $DIR/up.py --route_dir=$DIR --route_port=$PORT --environment=$ENV"
echo Port: $PORT, environment $ENV

function handleSigChld() {
  sleep 1
  python3 $CMDLINE 2>&1 | $DIR/up-log.sh 'up.sh'
}
cd $1 || exit 1

trap handleSigChld SIGCHLD
set -o monitor

echo '-------------------------' | $DIR/up-log.sh up.sh
echo "python3 $CMDLINE" | $DIR/up-log.sh up.sh
echo '-------------------------' | $DIR/up-log.sh up.sh

python3 "CMDLINE" 2>&1 | $DIR/up-log.sh 'up.sh'


