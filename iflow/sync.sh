#!/bin/bash
# Sync command scripts and agents to ~/.iflow/

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Sync commands
COMMANDS_TARGET_DIR="$HOME/.iflow/commands"
mkdir -p "$COMMANDS_TARGET_DIR"
cp "$SOURCE_DIR/commands"/*.toml "$COMMANDS_TARGET_DIR/"
echo "Synced .toml files from $SOURCE_DIR/commands to $COMMANDS_TARGET_DIR"

# Sync agents
AGENTS_TARGET_DIR="$HOME/.iflow/agents"
mkdir -p "$AGENTS_TARGET_DIR"
cp "$SOURCE_DIR/agents"/*.md "$AGENTS_TARGET_DIR/"
echo "Synced .md files from $SOURCE_DIR/agents to $AGENTS_TARGET_DIR"
