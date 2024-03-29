#!/bin/python3

import sys

num_lower_bound = ord('0')
num_upper_bound = ord('9')
alpha_lower_bound = ord('a')


def tobin(n: int) -> str:
    if n < 10:
        c = chr(num_lower_bound + n)
    else:
        c = chr(alpha_lower_bound + n - 10)
    return c


if __name__ == '__main__':
    args = sys.argv[1:]

    num = int(args[0])
    n = num

    s = ''
    while num > 0:
        rem = num % 2
        s = tobin(rem) + s
        num = int(num / 2)

    print(f"dec: \"{n}\" to bin: \"{s}\"")
