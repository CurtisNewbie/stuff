
from genericpath import exists
import os
import sys
import re


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(0)

    l = sys.argv[1:]
    for i in range(len(l)):
        f = l[i]
        if not exists(f):
            print(f"file {f} not found")
            sys.exit(1)

        ff = re.sub("[ \\-）（\\(\\),\'_+]+", "_", f.strip())
        if len(ff) > 1 and ff[0] == "_":
            ff = ff[1:]

        if f == ff:
            sys.exit(0)

        os.rename(f, ff)
        print(f"renamed from '{f}' to '{ff}'")
