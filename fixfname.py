
from genericpath import exists
import os
import sys
import re


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(0)

    f = sys.argv[1]
    if not exists(f):
        print(f"file {f} not found")
        sys.exit(1)

    ff = re.sub("[ \\-）（]", "_", f.strip())
    ff = re.sub("_+", "_", ff)
    os.rename(f, ff)
    print(f"renamed from '{f}' to '{ff}'")
