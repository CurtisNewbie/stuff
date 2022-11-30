import sys

def print_help() -> None:
    """
    Print help
    """
    print("$TEXT $START $END")


"""
sub.py

yongj.zhuang
"""
if __name__ == '__main__':
    args = sys.argv[1:]
    # print(f"args: {args}")

    la = len(args)
    if la == 0:
        print_help()
        sys.exit(0)

    s = args[0]
    slen = len(s)

    lo = int(args[1]) if la > 1 and args[1] else 0 
    hi = int(args[2]) if la > 2 and args[2] else slen 
    if hi > slen:
        hi = slen

    print(s[lo: hi])
