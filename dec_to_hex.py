#!/bin/python3

import sys
import math

num_lower_bound = ord('0')
num_upper_bound = ord('9')
alpha_lower_bound = ord('a')

def to_hex(n: int) -> str:
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
        rem = num % 16
        s = to_hex(rem) + s 
        num = int(num / 16)

    print(f"dec: \"{n}\" to hex: \"{s}\"")




