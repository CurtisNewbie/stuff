# OpenCode Configuration Repository Usage Guide

This document records the setup and usage knowledge for the opencode configuration repository.

**Repository Purpose**:
- Centralized management of opencode project configurations, commands, skills, and plugins
- Provides a versionable configuration management solution
- Supports synchronization to the global opencode environment (~/.opencode/ and ~/.config/opencode/)

**Main Components**:
- AGENTS.md - agent configuration and user requirements
- commands/ - custom command definitions
- skills/ - custom agent skills
- opencode.jsonc - opencode core configuration
- sync.sh - synchronization script
- plugin/ - plugin-related configuration
- oh-my-opencode-slim.json - oh-my-opencode-slim configuration preset

---

## Oh My OpenCode Slim Installation

**Description**: oh-my-opencode-slim is a multi-agent programming system that provides specialized agent roles for OpenCode (orchestrator, oracle, librarian, explorer, designer, fixer), significantly improving programming efficiency.

### Installation Steps

1. **Run the installer** (recommended non-interactive mode):

```bash
bunx oh-my-opencode-slim@latest install --no-tui --tmux=no --skills=yes
```

**Option descriptions**:
- `--no-tui`: non-interactive mode
- `--tmux=no`: do not install tmux integration
- `--skills=yes`: install preset skills
- `--reset`: force override existing configuration (creates `.bak` backup)

2. **Authenticate with provider**:

```bash
opencode auth login
```

Select your provider and complete the OAuth flow.

3. **Verify installation**:

```bash
opencode
ping all agents
```

Confirm that all agents respond correctly.

### Configuration File Notes

- **Current preset**: `oh-my-opencode-slim.json` - configuration preset in this repository
- **Actual usage**: `~/.config/opencode/oh-my-opencode-slim.json` - global configuration after installation
- **Post-installation update**: by default, existing configuration files are not overwritten during installation; use `--reset` to force override (automatic backup)

**Note**: After installation, `~/.config/opencode/oh-my-opencode-slim.json` is updated based on system configuration and may differ from the preset file in the repository. When adjusting configuration, modify the global configuration file.

---

## Notification System (kdco/notify)

Push system notifications when AI tasks complete, encounter errors, or require permissions.

**Important**: This plugin should be installed globally, not locally for the project.

**Detailed documentation**: See [ocx-notify.md](./ocx-notify.md) for complete installation steps, configuration options, and usage instructions.

---

## Feishu/Lark Document Support (lark-cli)

If you need to read, write, or edit Feishu/Lark documents, messages, calendars, etc., you can configure the Feishu official CLI tool and skills.

### Installation Steps

```bash
# 1. Install CLI tool
npm install -g @larksuite/cli

# 2. Install CLI Skills (required)
npx skills add larksuite/cli -y -g

# 3. Configure app credentials (user completes in browser)
lark-cli config init --new

# 4. Login authentication (user completes in browser)
lark-cli auth login --recommend
```

### Main Skills

- `lark-doc` - create, read, update, search documents (Markdown-based)
- `lark-im` - send/reply messages, group chat management, message search, file upload/download
- `lark-calendar` - schedule viewing, event creation, meeting arrangement
- 17 other skills (sheets, base, tasks, mail, wiki, etc.)

**Official documentation**: https://github.com/larksuite/cli

**Note**: If you don't need to interact with Feishu/Lark, you can skip this configuration.