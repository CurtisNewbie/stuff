#!/bin/python3

from pandas.io.clipboard import clipboard_get
import sys
import re


def unquote(s: str) -> str:
    return s.strip().replace('\"', '').replace('\'', '')


def unquotejoin_text(text: str) -> None:
    # print(f"txt: {text}")

    lines = re.split("[,，.()]", text.strip())
    unquotejoin_lines(lines)


def unquotejoin_lines(lines: list[str]) -> None:
    if not lines:
        sys.exit()

    lines = list(filter(lambda x: x if x else None,  lines))
    # print(f"lines: {lines}")

    for i in range(len(lines)):
        lines[i] = unquote(lines[i])

    """
    lastline = lines[len(lines) - 1]
    if lines[0][0] == "(" and lastline[len(lastline) - 1] == ")":
        lines[0] = lines[0][1:]

        print(f"lastline: {lastline}, len(lastline): {len(lastline)}")
        lines[len(lines)] = lastline[:len(lastline) -
                                     1] if len(lastline) > 1 else ""
    """

    for i in range(len(lines)):
        print(lines[i])


def get_clipboard_text():
    return clipboard_get()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        txt = get_clipboard_text()
        if txt:
            unquotejoin_text(txt)
    else:
        lines = sys.argv[1:]
        if lines:
            unquotejoin_lines(sys.argv[1:])
