from curl_cffi import requests
import bs4
import argparse
import os, sys
import time

ap = argparse.ArgumentParser(description="ososk.py 2.0 by yongjie.zhuang", formatter_class=argparse.RawTextHelpFormatter)
ap.add_argument('-u', '--url', type=str, help=f"site url", required=True)
ap.add_argument('--proxy', type=str, help=f"http(s) proxy server", required=False)
ap.add_argument('--skip_mkdir', help=f"do not create new directory for the gallery", required=False, action="store_true", default=False)
args = ap.parse_args()

print(f"Parsing {args.url} using proxy: {args.proxy}")

proxies = {
  "http": args.proxy,
  "https": args.proxy,
}
html = requests.get(args.url, impersonate="chrome", proxies=proxies).text
# print(html)

soup = bs4.BeautifulSoup(html, 'html.parser')
ttitle: "bs4.Tag" = soup.find("title")
title = ttitle.text

import re
title = re.sub("[_ \-,.\(\)\']+", "_", title.strip())
print(f"\n---\nTitle: '{title}'")

hrefs = []
for a in soup.find_all('a', attrs={"data-fancybox" : "gallery"}):
    h = a.get('href')
    if h:
        # print(h)
        r = h.rfind("-")
        if r > -1:
            n: str = h[r+1:]
            n = n.replace("/", "-")
        else:
            r = h.rfind("/")
            n = h[r+1:]

        hrefs.append([h, n])
    else:
        imgs = a.findAll("img", recursive=False)
        for im in imgs:
            h: str = im.get('src')
            nh = h
            q = nh.find("?")
            if q > -1: nh = nh[:q]
            n = nh[nh.rfind("/")+1:]
            hrefs.append([h, n])

print("\n----\nhtml parsed: ")
for i, v in enumerate(hrefs):
    print(f"{i} - '{v}'")

dir = title
if not args.skip_mkdir:
    try:
        os.mkdir(dir)
    except FileExistsError:
        print(f"Directory '{dir}' already existed")
        pass
else:
    dir = None

print("\n----\ndownloading images: ")
for h, n in hrefs:
    if not h: continue
    if dir is not None:
        p = os.path.join(dir, n)
    else:
        p = n

    if os.path.exists(p):
        print(f"'{h}' already downloaded as '{p}'")
        continue

    try:
        with open(p, "wb") as df:
            start = time.monotonic_ns()
            response = requests.get(h, impersonate="chrome", timeout=20, proxies= proxies)
            df.write(response.content)
            print(f"Downloaded '{h}' as '{p}' ({(time.monotonic_ns() - start) / 1e9:.3}s)")
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Failed to download '{h}', error: {e}")