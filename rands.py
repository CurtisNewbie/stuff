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

# is BOTH or 
def is_both_or(s: str, target: str) -> bool:
    return s == BOTH or s == target

# build charset based on provided options
def buildcharset(charset: str, case: str) -> str:
    if case not in case_set:
        case = BOTH
    if charset not in charset_set:
        charset = BOTH

    s = ""
    charset = charset.lower()

    if is_both_or(charset, ALPHA):
        if case == BOTH or case == LOWER:
            for i in range(26):
                s = s + chr(i + ord('a'))

        if is_both_or(case, UPPER):
            for i in range(26):
                s = s + chr(i + ord('A'))

    if is_both_or(charset, NUMERIC):
        for i in range(10):
            s = s + chr(i + ord('0'))
    return s


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-l', '--length', type=int,
                        help=f"Length", required=False, default=DEFAULT_LEN)
    parser.add_argument('-t', '--times', type=int,
                        help=f"Number of random str", required=False, default=1)

    csj = "/".join([ALPHA, NUMERIC, BOTH])
    parser.add_argument('-s', '--charset', type=str,
                        help=f"Charset: {csj}", required=False, default=BOTH)

    csj = "/".join([UPPER, LOWER, BOTH])
    parser.add_argument('-c', '--case', type=str,
                        help=f"Case: {csj}", required=False, default=BOTH)
    parser.add_argument('-p', '--prefix', type=str,
                        help=f"Prefix", required=False, default="")
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()
    len = args.length
    times = args.times

    letters = buildcharset(args.charset, args.case)
    prefix = args.prefix

    for i in range(times):
        print(prefix + ''.join(random.choice(letters) for i in range(len)))
