#!/bin/python3

from pandas.io.clipboard import clipboard_get
import sys
import re


def quote(s: str) -> str:
    s = s.strip()
    return '\"' + s + '\"'

def quote_join_text(txt : str) -> None:
    lines = re.split("[\t\n]", txt)
    # print(f"lines {lines}")
    quote_join_lines(lines)

def quote_join_lines(args: list[str]) -> None:
    args = list(filter(lambda a: a if a else None, args))

    c = 0
    tbj = []
    for j in range(len(args)):
        arr = args[j].split(' ')
        for i in range(len(arr)):
            c = c + 1
            # print(f'[{c}] - {arr[i]}')
            tbj.append(quote(arr[i]))

    print("(" + ",".join(tbj) + ")\n")


def get_clipboard_text():
    return clipboard_get()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        txt = get_clipboard_text()
        if txt:
            quote_join_text(txt)
    else:
        lines = sys.argv[1:]
        if lines: 
            quote_join_lines(lines)

