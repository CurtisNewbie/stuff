#!/usr/bin/env bash
# Show top CPU consumers (and GPU if possible) on macOS.
# Usage: ./topcpu.sh [count]   (default 10)

set -euo pipefail
COUNT="${1:-10}"

echo "== Load: $(uptime | sed 's/.*load averages*: //')"
echo

echo "== Top ${COUNT} CPU consumers (current, 2-sample delta) =="
printf "%-7s %6s %6s %9s  %s\n" PID %CPU MEM TIME COMMAND
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

# top's command column truncates at 80 cols when piped, so grab PIDs from
# top (live CPU) and merge in full command lines from ps.
top -l 2 -o cpu -n "$COUNT" -stats pid,cpu,mem,time,command -s 1 \
    | awk '/^PID/{n++} n>=2 && $1 ~ /^[0-9]+\*?$/ { gsub(/\*$/, "", $1); print }' > "$tmp"

if [ -s "$tmp" ]; then
    pids=$(awk '{print $1}' "$tmp" | paste -sd, -)
    ps -p "$pids" -o pid= -o command= | awk '
        NR==FNR {
            cmd = $0
            sub(/^[ \t]+/, "", cmd)     # strip ps padding
            sub(/^[0-9]+ /, "", cmd)    # strip pid field
            split(cmd, a, " ")
            nb = split(a[1], pc, "/")
            base = pc[nb]
            rest = cmd
            sub(/^[^ ]* /, "", rest)    # drop path, keep args
            if (rest == cmd) map[$1] = base
            else map[$1] = base " " rest
            next
        }
        $1 != 0 && map[$1] != "" { printf "%-7s %6s %6s %9s  %s\n", $1, $2, $3, $4, map[$1] }
    ' - "$tmp" | cut -c1-180
fi
