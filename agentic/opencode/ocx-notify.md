# OCX + kdco/notify 安装指南

## 概览

- **OCX**：OpenCode 扩展管理器，采用 ShadCN 模型，将组件直接复制到项目的 `.opencode/` 目录（非 `node_modules`），可自由修改，SHA-256 校验完整性。
- **kdco/notify**：原生 OS 通知插件，在 AI 任务完成、出错或需要权限时推送系统通知。

---

## 一、安装 OCX

```bash
# macOS / Linux（推荐，自动处理 PATH 配置）
curl -fsSL https://ocx.kdco.dev/install.sh | sh

# 或通过 npm（全平台）
npm install -g ocx
```

安装目标：`/usr/local/bin/ocx`（macOS arm64 当前版本 v2.0.2）

---

## 二、初始化 OCX

在需要使用插件的项目目录执行：

```bash
ocx init
```

生成文件：
- `.opencode/ocx.jsonc` — OCX 配置（registry、锁定策略）
- `.opencode/opencode.jsonc` — OpenCode 项目配置

全局初始化（配置放在 `~/.config/opencode/`）：

```bash
ocx init --global
```

---

## 三、安装 kdco/notify 组件

```bash
ocx add kdco/notify --from https://registry.kdco.dev
```

安装结果（2 个组件）：

```
.opencode/plugins/
├── notify.ts              # 主插件入口，export default NotifyPlugin
├── notify/                # notify 内部模块
│   ├── backend.ts         # 通知后端，cmux 优先 + node-notifier 回退
│   ├── cmux.ts            # cmux CLI 通知支持
│   ├── get-project-id.ts
│   ├── index.ts
│   ├── log-warn.ts
│   ├── mutex.ts
│   ├── shell.ts
│   ├── temp.ts
│   ├── terminal-detect.ts
│   ├── types.ts
│   └── with-timeout.ts
└── kdco-primitives/       # 公共类型依赖
    └── types.ts
```

运行时依赖（自动注入到 `.opencode/package.json`）：

```json
{
  "devDependencies": {
    "node-notifier": "10.0.1",
    "detect-terminal": "2.0.0"
  }
}
```

---

## 四、插件工作原理

### 触发事件

| 事件 | 通知标题 | 触发条件 |
|------|----------|----------|
| `session.idle` | Ready for review | AI 任务完成，等待用户 review |
| `session.error` | Something went wrong | 会话出错 |
| `permission.updated` | Waiting for you | AI 需要权限审批 |
| `tool.execute.before`（question 工具）| Question for you | AI 提问 |

### 通知抑制逻辑

- **终端已聚焦**：用户正在看终端时不发送（避免打扰）
- **Quiet Hours**：配置免打扰时段（默认关闭）
- **子 Session**：默认只通知父 Session，子任务不发垃圾通知

### 通知后端优先级

```
cmux CLI（如在 cmux 环境中）
  └─> 成功则结束
  └─> 失败则 fallback

node-notifier
  ├─ macOS: terminal-notifier（点击通知可跳转回终端）
  ├─ Windows: SnoreToast
  └─ Linux: notify-send
```

---

## 五、自定义配置

配置文件路径：`~/.config/opencode/kdco-notify.json`

```json
{
  "notifyChildSessions": false,
  "sounds": {
    "idle": "Glass",
    "error": "Basso",
    "permission": "Submarine",
    "question": "Submarine"
  },
  "quietHours": {
    "enabled": true,
    "start": "22:00",
    "end": "08:00"
  },
  "terminal": "ghostty"
}
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `notifyChildSessions` | `false` | 是否对子 Session 也发通知 |
| `sounds.idle` | `"Glass"` | 任务完成音效（macOS 系统音效名） |
| `sounds.error` | `"Basso"` | 出错音效 |
| `sounds.permission` | `"Submarine"` | 权限请求音效 |
| `sounds.question` | 同 permission | 提问音效 |
| `quietHours.enabled` | `false` | 是否启用免打扰时段 |
| `quietHours.start` | `"22:00"` | 免打扰开始时间（HH:MM） |
| `quietHours.end` | `"08:00"` | 免打扰结束时间（HH:MM） |
| `terminal` | 自动检测 | 手动指定终端（覆盖自动检测） |

支持的 terminal 值：`ghostty`、`kitty`、`iterm2`、`wezterm`、`alacritty`、`terminal`、`warp`、`vscode` 等。

---

## 六、常用 OCX 命令速查

```bash
# 初始化
ocx init                                  # 项目级初始化
ocx init --global                         # 全局初始化

# 安装组件
ocx add kdco/notify --from https://registry.kdco.dev

# 添加 registry 别名后安装（更简洁）
ocx registry add https://registry.kdco.dev --name kdco
ocx add kdco/notify

# Profile 管理
ocx profile add <name> --source <registry/profile> --from <url> --global
ocx profile list --global
ocx oc -p <profile>                       # 用指定 profile 启动 OpenCode

# 其他
ocx config edit --global
ocx migrate                               # 预览 v1.4.6 → v2 迁移
ocx migrate --apply                       # 执行迁移
ocx verify                                # 校验完整性
```

---

## 七、与 opencode.json 配置集成

OCX 组件（本地插件）自动从 `.opencode/plugins/` 加载，**无需在 `opencode.json` 的 `plugin` 数组中声明**。

OpenCode 加载顺序：

1. `~/.config/opencode/opencode.json`（全局 npm 插件）
2. `opencode.json`（项目 npm 插件）
3. `~/.config/opencode/plugins/`（全局本地插件）
4. `.opencode/plugins/`（项目本地插件）← OCX 组件安装到这里

---

## 八、Registry 说明

- `https://registry.kdco.dev` — KDCO 官方 registry，提供 `notify`、`workspace` 等组件
- `https://tweakoc.com/r` — TweakOC registry，提供预构建 profile

OCX 使用 SHA-256 验证所有下载内容，保证安全性。
