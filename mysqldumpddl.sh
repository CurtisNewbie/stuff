#!/bin/bash
# dump-ddl.sh - Dump all table DDL from a MySQL database
set -euo pipefail
usage() {
  echo "Usage: $0 -h host -u user -p password -d database [-P port] [-o output.sql]"
  exit 1
}

HOST="${HOST:-localhost}"
USER="${USER:-root}"
PASS="${PASS:-}"
DB="${DB:-}"
PORT="${PORT:-3306}"
OUTPUT="${OUTPUT:-}"

while getopts "h:u:p:d:P:o:" opt; do
  case $opt in
    h) HOST="$OPTARG" ;;
    u) USER="$OPTARG" ;;
    p) PASS="$OPTARG" ;;
    d) DB="$OPTARG" ;;
    P) PORT="$OPTARG" ;;
    o) OUTPUT="$OPTARG" ;;
    *) usage ;;
  esac
done

[[ -z "$HOST" || -z "$USER" || -z "$PASS" || -z "$DB" ]] && usage
CMD="mysqldump -h '$HOST' -P '$PORT' -u '$USER' -p'$PASS' \
  --no-data \
  --skip-triggers \
  --compact \
 --set-gtid-purged=OFF \
  --routines=false \
  '$DB'"
if [[ -n "$OUTPUT" ]]; then
  eval "$CMD" > "$OUTPUT"
  echo "DDL written to $OUTPUT"
else
  eval "$CMD"
fi
