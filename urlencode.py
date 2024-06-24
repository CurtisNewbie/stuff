import sys
import argparse
from urllib.parse import quote, unquote

ap = argparse.ArgumentParser()
ap.add_argument('-value')
ap.add_argument('-decode', action='store_true')
args = ap.parse_args()

v = args.value
if not v:
    sys.exit()

if args.decode:
    print(unquote(v))
else:
    print(quote(v))
