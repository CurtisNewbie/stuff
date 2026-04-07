# OpenCode DB Cleanup

## 为什么越来越慢

OpenCode 把所有 session 数据存在 SQLite：

```
~/.local/share/opencode/opencode.db
```

每次启动都会执行：
1. `PRAGMA wal_checkpoint(PASSIVE)` — 合并 WAL 文件，随 DB 大小线性变慢
2. `migrate(db, entries)` — 扫描所有历史 migration，DB 越大越慢

Part 表存的是实际 LLM 响应内容，每条约 5-7KB，积累快（subagent 会产生大量短命 session）。**没有任何自动清理机制。**

## 判断是否需要清理

```bash
# 查看 DB 大小（超过 100MB 就值得清理）
du -sh ~/.local/share/opencode/opencode.db*

# 查看 session/message/part 数量
sqlite3 ~/.local/share/opencode/opencode.db "
SELECT COUNT(*) as sessions FROM session;
SELECT COUNT(*) as messages FROM message;
SELECT COUNT(*) as parts FROM part;
"

# 查看各时间段分布
sqlite3 ~/.local/share/opencode/opencode.db "
SELECT
  COUNT(*) as total,
  SUM(CASE WHEN datetime(time_updated/1000,'unixepoch') < datetime('now','-7 days')  THEN 1 ELSE 0 END) as older_7d,
  SUM(CASE WHEN datetime(time_updated/1000,'unixepoch') < datetime('now','-14 days') THEN 1 ELSE 0 END) as older_14d,
  SUM(CASE WHEN datetime(time_updated/1000,'unixepoch') < datetime('now','-30 days') THEN 1 ELSE 0 END) as older_30d
FROM session;
"
```

## 清理步骤

直接运行项目根目录的脚本：

```bash
# 预览将删除哪些（可在 opencode 运行时执行）
./cleanup.sh --dry-run

# 执行清理（默认保留 7 天内的 session，需关闭 opencode）
./cleanup.sh

# 自定义保留窗口
./cleanup.sh --days 14
./cleanup.sh --days 30
```

脚本会自动完成：检查进程 → 删旧 session（CASCADE 清理 message/part）→ VACUUM 回收空间 → 打印前后对比。

### 手动操作（备用）

```bash
# 删除
sqlite3 ~/.local/share/opencode/opencode.db "
PRAGMA foreign_keys = ON;
DELETE FROM session
WHERE datetime(time_updated/1000, 'unixepoch') < datetime('now', '-7 days');
SELECT changes() || ' sessions deleted';
"

# 回收空间
sqlite3 ~/.local/share/opencode/opencode.db "VACUUM;"
```

## 注意事项

- **类型陷阱**：`time_updated` 是毫秒时间戳。SQLite 里 `strftime('%s', ...)` 返回 TEXT，与 INTEGER 比较会出错（永远为真）。必须用 `datetime(time_updated/1000, 'unixepoch') < datetime('now', '-N days')` 做字符串比较。
- **CASCADE 有效**：`message` 和 `part` 都配置了 `ON DELETE CASCADE`，删 session 会自动级联删除，无需手动清理子表。
- **不需要备份**：这些都是历史对话记录，没有生产数据价值。直接删即可。

## 效果参考

| 保留窗口 | 清理前 | 清理后 |
|---|---|---|
| 7 天 | 257MB / 443 sessions | 92MB / 122 sessions |

**建议频率**：每月清理一次，或 DB 超过 150MB 时清理。
