#!/bin/python3

import sys

if __name__ == '__main__':
    args = sys.argv[1:]
    s: str = str(args[0])
    slen: int = len(s)
    print(f"Target: '{s}'\nLength: {slen}")
