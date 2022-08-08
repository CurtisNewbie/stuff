import sys

if __name__ == '__main__':
    nargv = len(sys.argv)
    if nargv < 3:
        sys.exit(0)

    candidates: set[str] = set(sys.argv[1].split(","))
    curr = sys.argv[3:]
    if len(curr) < 1:
        print(" ".join(candidates))
        sys.exit(0)

    diff = candidates.difference(curr)
    print(" ".join(diff))
