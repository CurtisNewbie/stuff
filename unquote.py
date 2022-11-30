#!/bin/python3

from pandas.io.clipboard import clipboard_get
import sys
import re


def unquote(s: str) -> str:
    return s.replace('\"', '').replace('\'', '')

def unquote_text(text: str) -> None:
    # print(f"txt: {text}")

    lines = re.split("[\t\n]", text.strip())
    unquote_lines(lines)

def unquote_lines(lines: list[str]) -> None:
    # print(f"lines: {lines}")
    for i in range(len(lines)):
        lines[i] = unquote(lines[i])

    print(''.join(lines))

def get_clipboard_text():
    return clipboard_get()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        txt = get_clipboard_text()
        if txt:
            unquote_text(txt)
    else:
        lines = sys.argv[1:]
        if lines:
            unquote_lines(sys.argv[1:])
