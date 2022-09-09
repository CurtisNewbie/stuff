import argparse
import random

DEFAULT_LEN = 25


def buildcharset(charset: str, case: str) -> str:
    if case not in {"upper", "lower", "all"}:
        case = "all"
    if charset not in {"alpha", "numeric", "all"}:
        charset = "all"

    s = ""
    charset = charset.lower()

    if charset == "all" or charset == "alpha":
        if case == "all" or case == "lower":
            for i in range(26):
                s = s + chr(i + ord('a'))

        if case == "all" or case == "upper":
            for i in range(26):
                s = s + chr(i + ord('A'))

    if charset == "all" or charset == "numeric":
        for i in range(10):
            s = s + chr(i + ord('0'))
    return s


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-l', '--length', type=int,
                        help=f"length", required=False, default=DEFAULT_LEN)
    parser.add_argument('-t', '--times', type=int,
                        help=f"number of random str", required=False, default=1)
    parser.add_argument('-s', '--charset', type=str,
                        help=f"charset: numeric/alpha/all", required=False, default="all")
    parser.add_argument('-c', '--case', type=str,
                        help=f"case: upper/lower/all", required=False, default="all")
    parser.add_argument('-p', '--prefix', type=str,
                        help=f"prefix", required=False, default="")
    args = parser.parse_args()

    len = args.length
    times = args.times

    letters = buildcharset(args.charset, args.case)
    prefix = args.prefix

    for i in range(times):
        print(prefix + ''.join(random.choice(letters) for i in range(len)))
