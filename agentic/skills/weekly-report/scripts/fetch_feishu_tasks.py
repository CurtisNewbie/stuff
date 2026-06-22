#!/usr/bin/env python3
"""
从飞书项目需求 URL 批量提取后端开发任务数据（名称、估分/人天、排期、状态）。

用法：
  # 从甘特图视图自动发现本周需求
  python3 fetch_feishu_tasks.py --gantt https://project.feishu.cn/xxx/userGantt/VIEW_ID

  # 指定周（ISO 周一日期）
  python3 fetch_feishu_tasks.py --gantt https://... --week 2026-06-16

  # 手动指定 URL
  python3 fetch_feishu_tasks.py \\
    https://project.feishu.cn/xxxx/story/detail/123456

依赖：
  - chromedb 已安装（用于从 Chrome Default profile 提取 cookies）
  - macOS Keychain 中有 Chrome Safe Storage 密钥

输出：JSON，每个需求包含：
  - title: 需求标题
  - work_item_id: 需求 ID
  - tasks: 后端开发任务列表（名称、估分、状态、排期）
  - total_points: 总估分（人天）
"""

import sys
import json
import subprocess
import re
import urllib.request
import urllib.parse
import urllib.error
import datetime
import os

API_URL = "https://project.feishu.cn/goapi/v5/workitem/v1/demand_fetch"
CHROME_PROFILE = "Default"  # used by get_chrome_cookies


def get_chrome_cookies(domain_filter: str) -> dict:
    """从 Chrome Default profile 读取指定域名的 cookies。"""
    # 从 macOS Keychain 获取 Chrome 加密密钥
    key_result = subprocess.run(
        ["security", "find-generic-password", "-w", "-s", "Chrome Safe Storage", "-a", "Chrome"],
        capture_output=True, text=True
    )
    if key_result.returncode != 0:
        raise RuntimeError("无法从 Keychain 获取 Chrome Safe Storage 密钥")
    password = key_result.stdout.strip()

    profile_path = f"{subprocess.run(['sh','-c','echo $HOME'], capture_output=True, text=True).stdout.strip()}/Library/Application Support/Google/Chrome/{CHROME_PROFILE}"

    result = subprocess.run(
        ["chromedb", "-c", "-p", profile_path],
        capture_output=True, text=True,
        env={**__import__('os').environ, "BROWSER_PASSWORD": password}
    )
    if result.returncode != 0:
        raise RuntimeError(f"chromedb 失败: {result.stderr}")

    cookies = {}
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            c = json.loads(line)
            if domain_filter in c.get("domain", ""):
                cookies[c["name"]] = c["value"]
        except Exception:
            pass
    return cookies


def fetch_api(payload: dict, cookies: dict) -> dict:
    """直接调用飞书项目 API。"""
    csrf = cookies.get("meego_csrf_token", "")
    cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Cookie": cookie_str,
            "x-meego-csrf-token": csrf,
            "x-meego-from": "web",
            "x-lark-gw": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": "https://project.feishu.cn/",
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_work_item_id(url: str) -> int:
    m = re.search(r'/story/detail/(\d+)', url)
    if not m:
        raise ValueError(f"无法从 URL 提取 work_item_id: {url}")
    return int(m.group(1))


def ts_to_date(ts: int) -> str:
    return datetime.datetime.utcfromtimestamp(ts / 1000).strftime("%Y-%m-%d")


def fetch_story(work_item_id: int, project_key: str, cookies: dict) -> dict:
    """拉取一个需求的完整信息，包括标题和后端开发任务。"""
    # Step 1: 拉 first_screen 获取标题和 workflow nodes
    full_data = fetch_api({
        "project_key": project_key,
        "work_item_type_key": "story",
        "work_item_id": work_item_id,
        "modules": [{"key": "detail", "params": {"first_screen": True}}],
        "version": "2"
    }, cookies)

    biz = full_data.get("data", {}).get("biz_data", [])
    ui_data = full_data.get("data", {}).get("ui_data", [])

    workitem = next((b["value"] for b in biz if b["key"] == "workitem"), {})
    title = workitem.get("name", f"workitem_{work_item_id}")

    # 需求描述
    desc_entry = next((u for u in ui_data if u.get("uuid") == "description"), None)
    description = ""
    if desc_entry:
        rt = desc_entry.get("uiValue", {}).get("richText", {})
        if not rt.get("isEmpty", True):
            description = rt.get("docText", "").strip()

    # 找后端开发节点
    workflow = next((b["value"] for b in biz if b["key"] == "workflow_layout"), {})
    nodes = workflow.get("nodes", [])
    be_node = next((n for n in nodes if n.get("name") == "后端开发"), None)
    if not be_node:
        return {"title": title, "description": description, "work_item_id": work_item_id,
                "error": "未找到后端开发节点", "tasks": [], "total_points": 0}

    be_uuid = be_node["uuid"]

    # Step 2: 拉后端开发任务
    be_data = fetch_api({
        "project_key": project_key,
        "work_item_type_key": "story",
        "work_item_id": work_item_id,
        "modules": [{"key": "detail:workflow:node:task", "params": {"uuids": [be_uuid]}}],
        "version": "2"
    }, cookies)

    be_biz = be_data.get("data", {}).get("biz_data", [])
    task_entry = next((b for b in be_biz if b.get("key") == "node_task" and b.get("uuid") == be_uuid), None)
    raw_tasks = task_entry["value"]["data"] if task_entry else []

    tasks = []
    for t in raw_tasks:
        sched = t.get("task_schedule", {}) or {}
        start_ts = sched.get("estimate_start_time")
        end_ts = sched.get("estimate_finish_time")
        tasks.append({
            "name": t.get("name", ""),
            "status": t.get("work_item_status", {}).get("state_key", ""),
            "points": t.get("points") or 0,
            "assignee": (t.get("assignee") or [{}])[0].get("nickname", ""),
            "start": start_ts and ts_to_date(start_ts),
            "end": end_ts and ts_to_date(end_ts),
        })

    total_points = sum(t["points"] for t in tasks)
    return {
        "title": title,
        "description": description,
        "work_item_id": work_item_id,
        "tasks": tasks,
        "total_points": total_points,
    }


def get_project_key(work_item_id: int, project_simple: str, cookies: dict) -> str:
    """从第一个需求的 API 响应中提取 project_key。"""
    data = fetch_api({
        "project_simple_name": project_simple,
        "work_item_api_name": "story",
        "work_item_id": work_item_id,
        "modules": [{"key": "detail", "params": {"first_screen": True}}],
        "version": "2"
    }, cookies)
    biz = data.get("data", {}).get("biz_data", [])
    workitem = next((b["value"] for b in biz if b["key"] == "workitem"), {})
    return workitem.get("project_key") or workitem.get("owned_project", {}).get("project_key", "")


def get_week_range(week_start_str: str | None = None) -> tuple[datetime.date, datetime.date]:
    """返回周一到周日的日期范围。默认为当前周。"""
    if week_start_str:
        start = datetime.date.fromisoformat(week_start_str)
        start = start - datetime.timedelta(days=start.weekday())
    else:
        today = datetime.date.today()
        start = today - datetime.timedelta(days=today.weekday())
    end = start + datetime.timedelta(days=6)
    return start, end

def discover_urls_from_gantt(gantt_url: str, cookies: dict, week_start: datetime.date, week_end: datetime.date) -> tuple[list[str], str]:
    """从飞书项目个人甘特图 API 获取指定周的需求 URL，同时返回 project_key。

    端点: POST /goapi/v3/search/gantt/user_data
    project_key 优先从 FEISHU_PROJECT_KEY 环境变量读取；
    若未设置则用 project_simple（飞书 Open API 支持 simple_name 作为 project_key），
    并从 API 响应中提取真实 project_key 供后续调用使用。

    返回: (story_urls, project_key)
    """
    m = re.match(r'https://project\.feishu\.cn/([^/]+)/', gantt_url)
    if not m:
        raise ValueError(f"无效的 gantt URL: {gantt_url}")
    project_simple = m.group(1)

    user_key = cookies.get("meego_user_key", "")
    if not user_key:
        raise RuntimeError("Cookie 中未找到 meego_user_key，请确认已在 Chrome 中登录飞书项目")

    csrf = cookies.get("meego_csrf_token", "")
    cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())

    # 优先用环境变量；否则用 simple_name（Open API 支持两者互用）
    project_id = os.environ.get("FEISHU_PROJECT_KEY") or project_simple

    start_ts = int(datetime.datetime.combine(week_start, datetime.time.min).timestamp())
    end_ts = int(datetime.datetime.combine(week_end, datetime.time.max).timestamp())

    payload = {
        "filters": {},
        "sorts": [{"order": "ASC", "field_item": {"strategy": 0, "key": "score", "type": "score", "class": "field"}}],
        "person_scope_list": [{"type": "user", "id": user_key, "name": ""}],
        "user_keys": [],
        "data_source": [{
            "project_key": project_id,
            "work_item_type_sources": [{"work_item_type_key": "story", "unusual_actions": [], "work_item_type_name": "需求"}],
            "unusual_actions": [],
        }],
        "data_source_type": 0,
        "detail_count": 50,
        "filter_empty": False,
        "start_time": start_ts,
        "end_time": end_ts,
        "need_statistic": False,
        "only_authorized": False,
        "project_key": project_id,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://project.feishu.cn/goapi/v3/search/gantt/user_data",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Cookie": cookie_str,
            "x-meego-csrf-token": csrf,
            "x-meego-from": "web",
            "x-lark-gw": "1",
            "x-meego-scope": "userGantt",
            "x-meego-local": "28800",
            "x-meego-timezone": "28800/28800",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": gantt_url,
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"甘特图 API HTTP {e.code}: {body}") from None

    if result.get("code") != 0:
        raise RuntimeError(f"甘特图 API 错误: {result.get('msg')} (code={result.get('code')})")

    user_schedules = result.get("data", {}).get("user_schedules", [])

    # 从响应中提取真实 project_key（比 simple_name 更可靠，用于后续 fetch_story）
    project_key = project_id
    for schedule in user_schedules:
        for task in schedule.get("tasks", []):
            pk = task.get("work_item_info", {}).get("project", "")
            if pk:
                project_key = pk
                break
        if project_key != project_id:
            break

    ids = list(dict.fromkeys(
        str(task["work_item_info"]["work_item_id"])
        for schedule in user_schedules
        for task in schedule.get("tasks", [])
        if task.get("work_item_info", {}).get("work_item_id")
    ))
    return [f"https://project.feishu.cn/{project_simple}/story/detail/{wid}" for wid in ids], project_key


def main():
    args = sys.argv[1:]

    gantt_url = None
    if "--gantt" in args:
        idx = args.index("--gantt")
        if idx + 1 < len(args):
            gantt_url = args[idx + 1]
            args = args[:idx] + args[idx + 2:]

    week_str = None
    if "--week" in args:
        idx = args.index("--week")
        if idx + 1 < len(args):
            week_str = args[idx + 1]
            args = args[:idx] + args[idx + 2:]

    if not gantt_url:
        gantt_url = os.environ.get("FEISHU_GANTT_URL")

    if not gantt_url and not args:
        print("用法:")
        print("  python3 fetch_feishu_tasks.py --gantt <gantt_url> [--week YYYY-MM-DD]")
        print("  python3 fetch_feishu_tasks.py <story_url> [story_url ...]")
        print("  或设置环境变量 FEISHU_GANTT_URL")
        sys.exit(1)

    print("[info] 从 Chrome Default profile 读取 cookies...", file=sys.stderr)
    cookies = get_chrome_cookies("feishu.cn")
    if not cookies.get("meego_csrf_token"):
        print("ERROR: 未找到 meego_csrf_token，请确认已在 Chrome 中登录飞书项目", file=sys.stderr)
        sys.exit(1)
    print(f"[info] 已获取 {len(cookies)} 个 cookies", file=sys.stderr)

    week_start: datetime.date | None = None
    week_end: datetime.date | None = None
    project_key: str = ""

    if gantt_url:
        week_start, week_end = get_week_range(week_str)
        print(f"[info] 从甘特图视图获取需求（{week_start} ~ {week_end}）...", file=sys.stderr)
        urls, project_key = discover_urls_from_gantt(gantt_url, cookies, week_start, week_end)
        if not urls:
            print("ERROR: 甘特图 API 未返回任何本周需求", file=sys.stderr)
            sys.exit(1)
        print(f"[info] 发现 {len(urls)} 个需求，project_key: {project_key}", file=sys.stderr)
        for u in urls:
            print(f"  {u}", file=sys.stderr)
    else:
        urls = args
        m = re.search(r'project\.feishu\.cn/([^/]+)/', urls[0])
        if not m:
            print("ERROR: 无法从 URL 提取 project namespace", file=sys.stderr)
            sys.exit(1)
        project_simple = m.group(1)
        print(f"[info] 获取 project_key...", file=sys.stderr)
        project_key = get_project_key(extract_work_item_id(urls[0]), project_simple, cookies)
        if not project_key:
            print("ERROR: 无法获取 project_key", file=sys.stderr)
            sys.exit(1)
        print(f"[info] project_key: {project_key}", file=sys.stderr)

    work_item_ids = [extract_work_item_id(u) for u in urls]

    results = []
    skipped = 0
    week_start_iso = week_start.isoformat() if week_start else None
    week_end_iso = week_end.isoformat() if week_end else None

    for i, (url, wid) in enumerate(zip(urls, work_item_ids)):
        print(f"[{i+1}/{len(urls)}] 拉取需求 {wid}...", file=sys.stderr)
        story = fetch_story(wid, project_key, cookies)

        # gantt 模式：只保留有后端任务且排期结束在目标周内的需求
        if gantt_url and week_start_iso and week_end_iso:
            in_week = [
                t for t in story.get("tasks", [])
                if t.get("end") and week_start_iso <= t["end"] <= week_end_iso
            ]
            if not in_week:
                print(f"  ↳ 跳过（无本周内的后端任务）", file=sys.stderr)
                skipped += 1
                continue

        results.append(story)
        print(f"  ✓ {story['title']} — {story['total_points']} 人天", file=sys.stderr)

    if gantt_url:
        print(f"[info] 完成：{len(results)} 条需求，跳过 {skipped} 条（无本周任务）", file=sys.stderr)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
