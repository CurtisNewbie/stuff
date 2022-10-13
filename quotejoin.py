#!/bin/python3

import sys


def quote(s: str) -> str:
    s = s.strip()
    return '\"' + s + '\"'


def quote_join(args: list[str]) -> None:
    c = 0
    tbj = []
    for j in range(len(args)):
        arr = args[j].split(' ')
        for i in range(len(arr)):
            c = c + 1
            # print(f'[{c}] - {arr[i]}')
            tbj.append(quote(arr[i]))

    print("(" + ",".join(tbj) + ")")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(0)

    quote_join(sys.argv[1:])
