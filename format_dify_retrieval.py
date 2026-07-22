#!/usr/bin/env python3
import json
import os
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
    dify_prod_host = os.environ.get("DIFY_PROD_HOST", "").rstrip("/")

    for item in resources:
        title = item.get("datasetName", "")
        score = item.get("score", "")
        dataset_id = item.get("datasetId", "")
        document_id = item.get("documentId", "")
        content = item.get("content", "")
        document_path = f"/datasets/{dataset_id}/documents/{document_id}"
        full_path = f"{dify_prod_host}{document_path}" if dify_prod_host else ""
        indented_content = "\n".join(f"    {line}" for line in content.splitlines())
        lines = [
            f"标题: {title}\n"
            f"相关度: {score}\n"
            f"Dify文档Id: {document_id}\n"
        ]
        if full_path:
            lines.append(f"完整路径: {full_path}\n")
        else:
            lines.append(f"相对路径: {document_path}\n")
        lines.append(f"内容:\n{indented_content}")
        blocks.append("".join(lines))

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
