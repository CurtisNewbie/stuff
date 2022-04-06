from util import *
import sys

START_ARG = '-l'
END_ARG = '-h'
INPUT_ARG = '-i'


def print_help() -> None:
    """
    Print help
    """
    print(f"\n  sub.py by yongj.zhuang\n")
    print(f"  Arguments:\n")
    print(f"{TT}{INPUT_ARG}{T}string to be processed")
    print(f"{TT}{START_ARG}{T}starting index (0-based)")
    print(f"{TT}{END_ARG}{T}ending index\n")


"""
sub.py

yongj.zhuang
"""
if __name__ == '__main__':
    args = sys.argv[1:]

    # no arg provided
    if len(args) == 0:
        print_help()
        sys.exit(0)

    # parse args as context
    ctx = Context(args)

    assert_true(ctx.is_present(INPUT_ARG), f"{INPUT_ARG} for string to be processed must be specified")
    s = ctx.get_first(INPUT_ARG)

    slen = len(s)
    lo = int(ctx.get_first(START_ARG)) if ctx.is_present(START_ARG) else 0
    hi = int(ctx.get_first(END_ARG)) if ctx.is_present(END_ARG) else slen
    if hi > slen:
        hi = slen

    print(s[lo: hi])
