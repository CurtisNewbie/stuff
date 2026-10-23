#!/bin/bash
# Sync AGENTS_curr.md to ~/.config/opencode/ (opencode)

# Sync AGENTS.md
mkdir -p "$HOME/.config/opencode"
cp AGENTS_curr.md "$HOME/.config/opencode/AGENTS.md"
echo "Synced AGENTS_curr.md to $HOME/.config/opencode/AGENTS.md"

# cp AGENTS.md "$HOME/.opencode/"
# echo "Synced AGENTS.md to $HOME/.opencode/"
