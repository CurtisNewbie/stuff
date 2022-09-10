import argparse
import random

UPPER = "upper"
LOWER = "lower"
NUMERIC = "numeric"
ALPHA = "alpha"
DEFAULT_LEN = 25
BOTH = "both"

case_set = {UPPER, LOWER, BOTH}
charset_set = {ALPHA, NUMERIC, BOTH}


def buildcharset(charset: str, case: str) -> str:
    if case not in case_set:
        case = BOTH
    if charset not in charset_set:
        charset = BOTH

    s = ""
    charset = charset.lower()

    if charset == BOTH or charset == ALPHA:
        if case == BOTH or case == LOWER:
            for i in range(26):
                s = s + chr(i + ord('a'))

        if case == BOTH or case == UPPER:
            for i in range(26):
                s = s + chr(i + ord('A'))

    if charset == BOTH or charset == NUMERIC:
        for i in range(10):
            s = s + chr(i + ord('0'))
    return s


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-l', '--length', type=int,
                        help=f"length", required=False, default=DEFAULT_LEN)
    parser.add_argument('-t', '--times', type=int,
                        help=f"number of random str", required=False, default=1)

    csj = "/".join(charset_set)
    parser.add_argument('-s', '--charset', type=str,
                        help=f"charset: {csj}", required=False, default=BOTH)

    csj = "/".join(case_set)
    parser.add_argument('-c', '--case', type=str,
                        help=f"case: {csj}", required=False, default=BOTH)
    parser.add_argument('-p', '--prefix', type=str,
                        help=f"prefix", required=False, default="")
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()
    len = args.length
    times = args.times

    letters = buildcharset(args.charset, args.case)
    prefix = args.prefix

    for i in range(times):
        print(prefix + ''.join(random.choice(letters) for i in range(len)))
