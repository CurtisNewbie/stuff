#!/bin/python3

import sys

if __name__ == '__main__':
    args = sys.argv[1:]
    binstr = args[0]
    print(f"bin: \"{binstr}\" to dec: \"{int(binstr, 2)}\"")
