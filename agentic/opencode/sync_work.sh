#!/bin/bash
# Sync AGENTS_work.md to ~/.config/opencode/ (opencode)

# Sync AGENTS.md
mkdir -p "$HOME/.config/opencode"
cp AGENTS_work.md "$HOME/.config/opencode/AGENTS.md"
echo "Synced AGENTS_work.md to $HOME/.config/opencode/AGENTS.md"

# Sync cli.json
cp cli.json "$HOME/.config/opencode/cli.json"
echo "Synced cli.json to $HOME/.config/opencode/cli.json"

# cp AGENTS.md "$HOME/.opencode/"
# echo "Synced AGENTS.md to $HOME/.opencode/"
