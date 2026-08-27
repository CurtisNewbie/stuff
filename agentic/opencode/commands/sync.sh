#!/bin/bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="$HOME/.config/opencode/command"

mkdir -p "$DEST_DIR"
cp "$SRC_DIR"/*.md "$DEST_DIR"/

echo "Synced $(ls "$SRC_DIR"/*.md | wc -l | tr -d ' ') command file(s) to $DEST_DIR"
