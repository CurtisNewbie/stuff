import sys
import argparse
from urllib.parse import quote_plus, unquote_plus

ap = argparse.ArgumentParser()
ap.add_argument('-value')
ap.add_argument('-decode', action='store_true')
args = ap.parse_args()

v = args.value
if not v:
    sys.exit()

if args.decode:
    print(unquote_plus(v))
else:
    print(quote_plus(v))
