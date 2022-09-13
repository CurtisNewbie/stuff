#!/bin/python3

import sys
import math

num_lower_bound = ord('0')
num_upper_bound = ord('9')
alpha_lower_bound = ord('a')


def to_int(s: str) -> int:
    c = s.lower()[0]
    code = ord(c)
    if code < num_upper_bound:
        return code - num_lower_bound
    else:
        return code - alpha_lower_bound + 10


def to_hex(n: int) -> str:
    if n < 10:
        c = chr(num_lower_bound + n)
    else:
        c = chr(alpha_lower_bound + n - 10)
    return c


if __name__ == '__main__':
    args = sys.argv[1:]
    hx = args[0]
    if hx.startswith("0x"):
        hx = hx[2:]

    hl = len(hx)

    s = 0
    for i in range(hl):
        rev_i = hl - i - 1
        pv = math.pow(16, rev_i)
        s += to_int(hx[i]) * pv

    num = int(s)
    n = num

    s = ''
    while num > 0:
        rem = num % 2
        s = to_hex(rem) + s
        num = int(num / 2)

    print(f"hex: \"{hx}\" to bin: \"{s}\"")
