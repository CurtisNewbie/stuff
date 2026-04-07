#!/usr/bin/env bash
# cleanup.sh — 清理 OpenCode 历史 session，减小 DB 体积加快启动速度
# 用法: ./cleanup.sh [--days N] [--dry-run]

set -euo pipefail

DB="$HOME/.local/share/opencode/opencode.db"
DAYS=7
DRY_RUN=false

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --days) DAYS="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# 检查 DB 存在
if [[ ! -f "$DB" ]]; then
  echo "DB not found: $DB"
  exit 1
fi

# 检查 opencode 是否在运行
if pgrep -x opencode > /dev/null 2>&1; then
  if $DRY_RUN; then
    echo "WARNING: opencode is running (dry-run only, no changes will be made)"
  else
    echo "ERROR: opencode is running. Please close it first."
    exit 1
  fi
fi

# 统计当前状态
echo "=== Current DB Status ==="
sqlite3 -noheader "$DB" "
SELECT
  '  Sessions : ' || COUNT(*)                      FROM session;
SELECT '  Messages : ' || COUNT(*)                 FROM message;
SELECT '  Parts    : ' || COUNT(*)                 FROM part;
"
echo "  DB size  : $(du -sh "$DB" | cut -f1)"

# 预览将要删除的数量
TO_DELETE=$(sqlite3 -noheader "$DB" "
SELECT COUNT(*) FROM session
WHERE datetime(time_updated/1000, 'unixepoch') < datetime('now', '-${DAYS} days');
")
TO_KEEP=$(sqlite3 -noheader "$DB" "
SELECT COUNT(*) FROM session
WHERE datetime(time_updated/1000, 'unixepoch') >= datetime('now', '-${DAYS} days');
")

echo ""
echo "=== Cleanup Preview (keeping last ${DAYS} days) ==="
echo "  Sessions to delete : $TO_DELETE"
echo "  Sessions to keep   : $TO_KEEP"

if [[ "$TO_DELETE" -eq 0 ]]; then
  echo "Nothing to delete."
  exit 0
fi

if $DRY_RUN; then
  echo ""
  echo "(dry-run mode, no changes made)"
  exit 0
fi

# 确认
echo ""
read -r -p "Proceed? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

# 执行删除
echo ""
echo "=== Deleting old sessions... ==="
sqlite3 -noheader "$DB" "
PRAGMA foreign_keys = ON;
DELETE FROM session
WHERE datetime(time_updated/1000, 'unixepoch') < datetime('now', '-${DAYS} days');
SELECT '  Deleted : ' || changes() || ' sessions';
"

# VACUUM
echo "=== Running VACUUM... ==="
sqlite3 "$DB" "VACUUM;"

# 最终状态
echo ""
echo "=== After Cleanup ==="
sqlite3 -noheader "$DB" "
SELECT '  Sessions : ' || COUNT(*)  FROM session;
SELECT '  Messages : ' || COUNT(*)  FROM message;
SELECT '  Parts    : ' || COUNT(*)  FROM part;
"
echo "  DB size  : $(du -sh "$DB" | cut -f1)"
echo "Done."
