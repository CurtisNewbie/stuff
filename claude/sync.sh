#!/bin/bash
# Sync commands and skills to ~/.claude/ (Claude Code)

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Sync commands
COMMANDS_TARGET_DIR="$HOME/.claude/commands"
mkdir -p "$COMMANDS_TARGET_DIR"
cp "$SOURCE_DIR/commands"/*.md "$COMMANDS_TARGET_DIR/" 2>/dev/null || true
echo "Synced commands from $SOURCE_DIR/commands to $COMMANDS_TARGET_DIR"

# Sync skills
SKILLS_TARGET_DIR="$HOME/.claude/skills"
mkdir -p "$SKILLS_TARGET_DIR"
for skill_dir in "$SOURCE_DIR/skills"/*/; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        mkdir -p "$SKILLS_TARGET_DIR/$skill_name"
        cp -r "$skill_dir"* "$SKILLS_TARGET_DIR/$skill_name/"
    fi
done
echo "Synced skills from $SOURCE_DIR/skills to $SKILLS_TARGET_DIR"

cp CLAUDE.md "$HOME/.claude/"