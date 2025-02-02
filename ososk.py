from curl_cffi import requests
import bs4
import argparse
import os
import time

ap = argparse.ArgumentParser(description="ososk.py 2.0 by yongjie.zhuang", formatter_class=argparse.RawTextHelpFormatter)
ap.add_argument('-u', '--url', type=str, help=f"site url", required=True)
ap.add_argument('--http_proxy', type=str, help=f"http proxy", required=False)
ap.add_argument('--https_proxy', type=str, help=f"https proxy", required=False)
args = ap.parse_args()

if args.http_proxy or args.https_proxy:
    print(f"Parsing {args.url} using proxy: {args.http_proxy}, {args.https_proxy}")
else:
    print(f"Parsing {args.url}")

proxies = {
  "http": args.http_proxy,
  "https": args.https_proxy,
}
html = requests.get(args.url, impersonate="chrome", proxies= proxies).text
# print(html)

soup = bs4.BeautifulSoup(html, 'html.parser')

hrefs = []
for a in soup.find_all('a', attrs={"data-fancybox" : "gallery"}):
    h = a.get('href')
    if h:
        print(h)
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

print("\n----\ndownloading images: ")
for h, n in hrefs:
    if not h: continue
    if os.path.exists(n):
        print(f"'{h}' already downloaded as '{n}'")
        continue

    try:
        with open(n, "wb") as df:
            start = time.monotonic_ns()
            response = requests.get(h, impersonate="chrome", timeout=20, proxies= proxies)
            df.write(response.content)
            print(f"Downloaded '{h}' as '{n}' ({(time.monotonic_ns() - start) / 1e9:.3}s)")
    except Exception as e:
        print(f"Failed to download '{h}', error: {e}")