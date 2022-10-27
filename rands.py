import argparse
import random

UPPER = "upper"
LOWER = "lower"
NUMERIC = "numeric"
ALPHA = "alphabetic"
SYMBOLS = "!@#$%&*"
DEFAULT_LEN = 25
ALL = "all"

case_set = {UPPER, LOWER, ALL}
charset_set = {ALPHA, NUMERIC, ALL}


def is_all_or(s: str, target: str) -> bool:
    '''
    is ALL or
    '''
    return s == ALL or s == target


def buildcharset(charset: str, case: str, include_symbols: bool) -> str:
    '''
    build charset based on provided options
    '''
    charset = charset.lower()
    case = case.lower()

    if case not in case_set:
        case = ALL
    if charset not in charset_set:
        charset = ALL

    s = ""
    charset = charset.lower()

    if is_all_or(charset, ALPHA):
        if is_all_or(case, LOWER):
            for i in range(26):
                s = s + chr(i + ord('a'))

        if is_all_or(case, UPPER):
            for i in range(26):
                s = s + chr(i + ord('A'))

    if is_all_or(charset, NUMERIC):
        for i in range(10):
            s = s + chr(i + ord('0'))

    if include_symbols:
        s = s + SYMBOLS

    return s


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-l', '--length', type=int,
                        help=f"Length", required=False, default=DEFAULT_LEN)
    parser.add_argument('-t', '--times', type=int,
                        help=f"Number of random str", required=False, default=1)

    csj = "/".join([ALPHA, NUMERIC, ALL])
    parser.add_argument('-s', '--charset', type=str,
                        help=f"Charset: {csj}", required=False, default=ALL)
    parser.add_argument('-b', '--symbol', type=str,
                        help="Include symbols", required=False, default='false')

    csj = "/".join([UPPER, LOWER, ALL])
    parser.add_argument('-c', '--case', type=str,
                        help=f"Case: {csj}", required=False, default=ALL)
    parser.add_argument('-p', '--prefix', type=str,
                        help=f"Prefix", required=False, default="")
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()
    len = args.length
    times = args.times

    letters = buildcharset(args.charset, args.case, args.symbol.lower() == 'true')
    prefix = args.prefix

    for i in range(times):
        print(prefix + ''.join(random.choice(letters) for i in range(len)))
