#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys


def read_clipboard() -> str:
    if shutil.which("pbpaste"):
        result = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True)
        return result.stdout
    if shutil.which("xclip"):
        result = subprocess.run(
            ["xclip", "-selection", "clipboard", "-o"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    raise RuntimeError("clipboard reader not found: need pbpaste or xclip")


def write_clipboard(text: str) -> None:
    if shutil.which("pbcopy"):
        subprocess.run(["pbcopy"], input=text, text=True, check=True)
        return
    if shutil.which("xclip"):
        subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
        return
    raise RuntimeError("clipboard writer not found: need pbcopy or xclip")


def format_resources(data: dict) -> str:
    resources = data.get("resources", [])
    blocks = []

    for item in resources:
        title = item.get("datasetName", "")
        score = item.get("score", "")
        content = item.get("content", "")
        blocks.append(f"标题: {title}\n相关度: {score}\n内容: {content}")

    return "\n\n".join(blocks)


def main() -> None:
    try:
        raw = read_clipboard()
        data = json.loads(raw)
        formatted = format_resources(data)
        write_clipboard(formatted)
    except Exception as e:
        sys.exit(f"处理剪贴板 JSON 失败: {e}")

    print(formatted)


if __name__ == "__main__":
    main()
