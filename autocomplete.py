import sys

if __name__ == '__main__':
    nargv = len(sys.argv)
    if nargv < 3:
        sys.exit(0)

    candidates: set[str] = set(sys.argv[1].split(","))
    curr = sys.argv[2]
    if curr == "":
        print(" ".join(candidates))
        sys.exit(0)

    currset: set[str] = set(curr.split(" "))
    diff = candidates.difference(currset)
    #print(f"currset: {currset}, diff: {diff}")

    print(" ".join(diff))
