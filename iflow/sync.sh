#!/bin/bash
# Sync command scripts and agents to ~/.iflow/

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Sync commands
COMMANDS_TARGET_DIR="$HOME/.iflow/commands"
mkdir -p "$COMMANDS_TARGET_DIR"
cp "$SOURCE_DIR/commands"/*.toml "$COMMANDS_TARGET_DIR/"
echo "Synced .toml files from $SOURCE_DIR/commands to $COMMANDS_TARGET_DIR"

# Sync skills
SKILLS_TARGET_DIR="$HOME/.iflow/skills"
mkdir -p "$SKILLS_TARGET_DIR"
cp -r "$SOURCE_DIR/skills"/* "$SKILLS_TARGET_DIR/"
echo "Synced skills files from $SOURCE_DIR/skills to $SKILLS_TARGET_DIR"
