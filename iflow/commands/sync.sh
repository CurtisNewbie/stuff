#!/bin/bash
# Sync command scripts to ~/.iflow/commands

TARGET_DIR="$HOME/.iflow/commands"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Copy only .toml files from source to target
cp "$SOURCE_DIR"/*.toml "$TARGET_DIR/"

echo "Synced .toml files from $SOURCE_DIR to $TARGET_DIR"
