import argparse
import os
import time
import sys
import bs4
from requests_html import HTMLSession, HTML

'''
# https://github.com/psf/requests-html/issues/341
# headless mode affect the use of proxy :D
# .local/lib/python3.9/site-packages/requests_html.py

@property
async def browser(self):
    if not hasattr(self, "_browser"):
        self._browser = await pyppeteer.launch(ignoreHTTPSErrors=not(self.verify), headless=False, args=self.__browser_args)

    return self._browser
'''

session = HTMLSession()

def render(url: str, request_timeout, render_timeout, retries, wait, sleep) -> str:
    start = time.monotonic_ns()
    r = session.get(url, timeout=request_timeout)
    print(f"Rquested '{url}' ({(time.monotonic_ns() - start) / 1e9:.3}s)")

    start = time.monotonic_ns()
    rh: HTML = r.html
    rh.render(retries=retries, timeout=render_timeout, wait=wait, sleep=sleep)
    print(f"Rendered '{url}' ({(time.monotonic_ns() - start) / 1e9:.3}s)")

    return r.html.html


'''
pip install beautifulsoup4
pip install requests_html
'''
if __name__ == "__main__":

    ap = argparse.ArgumentParser(description="ososk.py by yongjie.zhuang", formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument('-f', '--file', type=str, help=f"input file with site urls", required=False)
    ap.add_argument('-u', '--url', action='append', type=str, help=f"site url", required=False)
    ap.add_argument('--retries', type=int, help=f"render retries, default 2", required=False, default=2)
    ap.add_argument('--requesttimeout', type=float, help=f"request timeout in seconds, default 10s", required=False, default=10)
    ap.add_argument('--rendertimeout', type=float, help=f"render timeout in seconds, default 60s", required=False, default=60)
    ap.add_argument('--wait', type=float, help=f"time wait before rendering web page in seconds, default 3s", required=False, default=3)
    ap.add_argument('--sleep', type=float, help=f"time sleep after initial render in seconds, default 0s", required=False, default=0)
    args = ap.parse_args()

    sites = []

    if args.file:
        with open(args.file) as f:
            all = f.read()
            sites = all.splitlines()

    if args.url:
        for au in args.url: sites.append(au)

    for url in sites:
        html = render(url, args.requesttimeout, args.rendertimeout, args.retries, args.wait, args.sleep)
        start = time.monotonic_ns()
        soup = bs4.BeautifulSoup(html, 'html.parser')
        print(f"BS4 parsed '{url}' ({(time.monotonic_ns() - start) / 1e9:.3}s)")

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

        for h, n in hrefs:
            if not h: continue

            if os.path.exists(n):
                print(f"'{h}' already downloaded as '{n}'")

            try:
                with open(n, "wb") as df:
                    start = time.monotonic_ns()
                    response = session.get(h, timeout=20)
                    df.write(response.content)
                    print(f"Downloaded '{h}' as '{n}' ({(time.monotonic_ns() - start) / 1e9:.3}s)")
            except Exception as e:
                print(f"Failed to download '{h}', error: {e}")