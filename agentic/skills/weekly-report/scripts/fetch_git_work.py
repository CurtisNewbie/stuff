#!/usr/bin/env python3
"""
扫描本周 Git 工作证据：本人提交和本周修改过的文件。

用法：
  python3 fetch_git_work.py
  python3 fetch_git_work.py --repo-root /path/to/work --week-start 2026-06-16

脚本只读取 Git 配置、历史和文件状态，不执行 fetch/pull/checkout，也不写入仓库或用户工作记录。
"""

from __future__ import annotations

import argparse
import datetime as datetime_module
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Any


DEFAULT_MAX_FILES = 200
GENERATED_DIRECTORIES = {
    ".cache",
    ".mypy_cache",
    ".next",
    ".nuxt",
    ".pytest_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "out",
    "target",
    "tmp",
    "temp",
    "venv",
    "node_modules",
}


def run_git(repo: Path, args: list[str]) -> subprocess.CompletedProcess[bytes]:
    """在指定仓库中执行只读 Git 命令。"""
    command = ["git", "-C", str(repo), *args]
    try:
        return subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, 124, b"", "git 命令超时".encode())


def decode_git_output(data: bytes) -> str:
    return os.fsdecode(data)


def is_git_repository(path: Path) -> bool:
    """仅依据仓库目录下的 .git 目录或 worktree .git 文件判断。"""
    try:
        return path.is_dir() and ((path / ".git").is_dir() or (path / ".git").is_file())
    except OSError:
        return False


def direct_repositories(parent: Path, warnings: list[str]) -> list[Path]:
    """只检查 parent 的直接子目录，不递归进入其他目录。"""
    if not parent.is_dir():
        return []

    try:
        children = sorted(parent.iterdir(), key=lambda item: item.name.casefold())
    except OSError as exc:
        warnings.append(f"无法读取目录 {parent}: {exc}")
        return []

    repositories = []
    for child in children:
        if child.name == ".git" or not child.is_dir():
            continue
        if is_git_repository(child):
            repositories.append(child)
    return repositories


def discover_repositories(root: Path, warnings: list[str]) -> list[Path]:
    """先扫描 aaas 下直接子目录仓库，再扫描根目录其他直接子目录仓库。"""
    priority = root / "aaas"
    repositories: list[Path] = []
    if is_git_repository(priority):
        # 兼容 aaas 本身就是单一项目仓库的布局。
        repositories.append(priority)
    elif priority.is_dir():
        repositories.extend(direct_repositories(priority, warnings))

    for repository in direct_repositories(root, warnings):
        if repository == priority:
            continue
        repositories.append(repository)
    return repositories


def read_identity(repository: Path, warnings: list[str]) -> tuple[str, str]:
    """读取当前仓库生效的 user.name 和 user.email。"""
    values: dict[str, str] = {}
    for key in ("user.name", "user.email"):
        try:
            result = run_git(repository, ["config", "--get", key])
        except OSError as exc:
            warnings.append(f"仓库 {repository} 无法读取 {key}: {exc}")
            continue
        if result.returncode == 0:
            values[key] = decode_git_output(result.stdout).strip()

    name = values.get("user.name", "")
    email = values.get("user.email", "")
    if not name or not email:
        missing = []
        if not name:
            missing.append("user.name")
        if not email:
            missing.append("user.email")
        warnings.append(f"仓库 {repository} 未配置生效的 {', '.join(missing)}，跳过本人提交匹配")
    return name, email


def is_generated_path(path: str) -> bool:
    return any(
        part.casefold() in GENERATED_DIRECTORIES
        for part in PurePosixPath(path).parts
    )


def local_timestamp(value: datetime_module.date) -> float:
    return datetime_module.datetime.combine(
        value, datetime_module.time.min
    ).timestamp()


def format_mtime(timestamp: float) -> str:
    return datetime_module.datetime.fromtimestamp(timestamp).astimezone().isoformat(timespec="seconds")


def scan_modified_files(
    repository: Path,
    week_start: datetime_module.date,
    week_end_exclusive: datetime_module.date,
    max_files: int,
    warnings: list[str],
) -> tuple[list[dict[str, str]], bool]:
    """扫描 tracked 和未被忽略的 untracked 文件的本周 mtime。"""
    try:
        result = run_git(repository, ["ls-files", "--cached", "--others", "--exclude-standard", "-z"])
    except OSError as exc:
        warnings.append(f"仓库 {repository} 无法读取文件列表: {exc}")
        return [], False
    if result.returncode != 0:
        detail = decode_git_output(result.stderr).strip()
        warnings.append(f"仓库 {repository} 无法读取文件列表: {detail or 'git ls-files 失败'}")
        return [], False

    start_timestamp = local_timestamp(week_start)
    end_timestamp = local_timestamp(week_end_exclusive)
    candidates: list[tuple[float, str]] = []
    paths = [decode_git_output(item) for item in result.stdout.split(b"\0") if item]
    for relative_path in paths:
        if is_generated_path(relative_path):
            continue
        path = repository / relative_path
        try:
            if not path.is_file() and not path.is_symlink():
                continue
            mtime = path.stat().st_mtime
        except OSError as exc:
            warnings.append(f"仓库 {repository} 无法读取文件 {relative_path}: {exc}")
            continue
        if start_timestamp <= mtime < end_timestamp:
            candidates.append((mtime, relative_path))

    candidates.sort(key=lambda item: (-item[0], item[1]))
    truncated = len(candidates) > max_files
    files = [
        {"path": relative_path, "mtime": format_mtime(mtime)}
        for mtime, relative_path in candidates[:max_files]
    ]
    return files, truncated


def commit_files(repository: Path, commit_hash: str, warnings: list[str]) -> list[str]:
    try:
        result = run_git(
            repository,
            ["diff-tree", "--no-commit-id", "--name-only", "-r", "--root", "-z", commit_hash],
        )
    except OSError as exc:
        warnings.append(f"仓库 {repository} 无法读取提交 {commit_hash} 涉及文件: {exc}")
        return []
    if result.returncode != 0:
        detail = decode_git_output(result.stderr).strip()
        warnings.append(
            f"仓库 {repository} 无法读取提交 {commit_hash} 涉及文件: "
            f"{detail or 'git diff-tree 失败'}"
        )
        return []
    return [decode_git_output(item) for item in result.stdout.split(b"\0") if item]


def scan_commits(
    repository: Path,
    week_start: datetime_module.date,
    week_end_exclusive: datetime_module.date,
    identity_name: str,
    identity_email: str,
    warnings: list[str],
) -> list[dict[str, Any]]:
    """按 author name/email 匹配本人提交，明确不按 committer 匹配。"""
    if not identity_name or not identity_email:
        return []

    since = f"{week_start.isoformat()} 00:00:00"
    before = f"{week_end_exclusive.isoformat()} 00:00:00"
    format_string = "%H%x00%an%x00%ae%x00%aI%x00%s"
    try:
        result = run_git(
            repository,
            [
                "log",
                "--all",
                f"--since-as-filter={since}",
                f"--before={before}",
                f"--format={format_string}",
            ],
        )
    except OSError as exc:
        warnings.append(f"仓库 {repository} 无法读取 Git 历史: {exc}")
        return []
    if result.returncode != 0:
        detail = decode_git_output(result.stderr).strip()
        warnings.append(f"仓库 {repository} 无法读取 Git 历史: {detail or 'git log 失败'}")
        return []

    expected_name = identity_name.casefold()
    expected_email = identity_email.casefold()
    commits: list[dict[str, Any]] = []
    for line in decode_git_output(result.stdout).splitlines():
        fields = line.split("\0", 4)
        if len(fields) != 5:
            if line.strip():
                warnings.append(f"仓库 {repository} 的 Git 历史存在无法解析的记录")
            continue
        commit_hash, author_name, author_email, author_date, subject = fields
        if (
            author_name.casefold() != expected_name
            or author_email.casefold() != expected_email
        ):
            continue

        commits.append(
            {
                "hash": commit_hash,
                "author": {"name": author_name, "email": author_email},
                "date": author_date,
                "subject": subject,
                "files": commit_files(repository, commit_hash, warnings),
            }
        )
    return commits


def relative_repository_path(repository: Path, root: Path) -> str:
    return repository.relative_to(root).as_posix()


def scan_repository(
    repository: Path,
    root: Path,
    week_start: datetime_module.date,
    week_end_exclusive: datetime_module.date,
    max_files: int,
    warnings: list[str],
) -> dict[str, Any] | None:
    identity_name, identity_email = read_identity(repository, warnings)
    modified_files, modified_files_truncated = scan_modified_files(
        repository,
        week_start,
        week_end_exclusive,
        max_files,
        warnings,
    )
    commits = scan_commits(
        repository,
        week_start,
        week_end_exclusive,
        identity_name,
        identity_email,
        warnings,
    )
    if not commits and not modified_files:
        return None

    return {
        "path": relative_repository_path(repository, root),
        "identity": {"name": identity_name, "email": identity_email},
        "commits": commits,
        "modified_files": modified_files,
        "modified_files_truncated": modified_files_truncated,
    }


def parse_week_start(value: str | None) -> datetime_module.date:
    date_value = (
        datetime_module.date.today()
        if value is None
        else datetime_module.date.fromisoformat(value)
    )
    return date_value - datetime_module.timedelta(days=date_value.weekday())


def positive_integer(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("必须是正整数") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("必须是正整数")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="扫描本周 Git 工作证据")
    parser.add_argument(
        "--repo-root",
        help="仓库根目录；未指定时读取 WORK_REPO_PATH",
    )
    parser.add_argument(
        "--week-start",
        help="周起始日期 YYYY-MM-DD；默认当前周周一",
    )
    parser.add_argument(
        "--max-files",
        type=positive_integer,
        default=DEFAULT_MAX_FILES,
        help=f"每个仓库最多输出多少条本周修改文件（默认 {DEFAULT_MAX_FILES}）",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    root_value = args.repo_root if args.repo_root is not None else os.environ.get("WORK_REPO_PATH")
    if not root_value:
        print(
            "错误：未提供仓库根目录，请设置 WORK_REPO_PATH 或使用 --repo-root PATH",
            file=sys.stderr,
        )
        return 2

    try:
        week_start = parse_week_start(args.week_start)
    except ValueError:
        parser.error("--week-start 必须是 YYYY-MM-DD 格式的日期")
        return 2

    root = Path(root_value).expanduser().resolve()
    if not root.is_dir():
        print(f"错误：仓库根目录不存在或不是目录：{root}", file=sys.stderr)
        return 2

    week_end = week_start + datetime_module.timedelta(days=4)
    week_end_exclusive = week_start + datetime_module.timedelta(days=5)
    warnings: list[str] = []
    repositories = discover_repositories(root, warnings)
    scan_order = [relative_repository_path(repository, root) for repository in repositories]
    scanned_results: list[dict[str, Any]] = []

    for repository in repositories:
        result = scan_repository(
            repository,
            root,
            week_start,
            week_end_exclusive,
            args.max_files,
            warnings,
        )
        if result is not None:
            scanned_results.append(result)

    output = {
        "week": {
            "start": week_start.isoformat(),
            "end": week_end.isoformat(),
        },
        "repo_root": str(root),
        "scan_order": scan_order,
        "scanned_repositories": scan_order,
        "repositories": scanned_results,
        "warnings": warnings,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
