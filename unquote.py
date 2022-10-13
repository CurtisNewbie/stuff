#!/bin/python3

import sys


def unquote(s: str) -> str:
    return s.replace('\"', '').replace('\'', '')


def unquoteall(lines: list[str]) -> None:
    for i in range(len(lines)):
        lines[i] = unquote(lines[i])

    print(''.join(lines))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(0)

    unquoteall(sys.argv[1:])
