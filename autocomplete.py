import sys

if __name__ == '__main__':
    nargv = len(sys.argv)

    candidates: set[str] = set(sys.argv[1].split(","))
    if len(sys.argv) < 2 or sys.argv[2] == "":
        print(" ".join(sorted(candidates)))
        sys.exit(0)

    curr = sys.argv[2]

    currset: set[str] = set(curr.split(" "))
    diff = candidates.difference(currset)
    #print(f"currset: {currset}, diff: {diff}")

    print(" ".join(sorted(diff)))
