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

if __name__ == '__main__':
    args = sys.argv[1:]
    hx = args[0]
    hl = len(hx)

    s = 0
    for i in range(hl):
        rev_i = hl - i - 1 
        pv = math.pow(16, rev_i)
        s += to_int(hx[i]) * pv 

    print(f"hex: \"{hx}\" to dec: \"{int(s)}\"")




