from curl_cffi import requests
import os, sys
from bs4 import BeautifulSoup

import argparse
ap = argparse.ArgumentParser(description="", formatter_class=argparse.RawTextHelpFormatter)
ap.add_argument("-f", type=str, help=f"file", required=True)
args = ap.parse_args()

file = args.f
with open(file, "r") as f:
    lines = f.readlines()
    for l in lines:
        l = l.strip()
        if not l: continue

        try:
            r = requests.get(l)
            r.raise_for_status()

            title_tag = BeautifulSoup(r.content, 'html.parser').find('title')
            title = ""
            if title_tag:
                title = title_tag.text.strip()

            print(f"- [{title}]({l})")
        except Exception as e:
            print(f"{l}, {e}")
