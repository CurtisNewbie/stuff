import os
import time 
import sys
import bs4
from requests_html import HTMLSession

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

def render(url: str, timeout = 20, retries = 2, wait = 3, sleep = 0) -> str:
    start = time.monotonic_ns()
    r = session.get(url, timeout=timeout)
    print(f"Rquested '{url}' ({(time.monotonic_ns() - start) / 1e9:.3}s)")

    start = time.monotonic_ns()
    r.html.render(retries=retries, timeout=timeout, wait=wait, sleep=sleep)
    print(f"Rendered '{url}' ({(time.monotonic_ns() - start) / 1e9:.3}s)")
    return r.html.html


'''
pip install beautifulsoup4
pip install requests_html
'''
if __name__ == "__main__":
    argv = sys.argv[1:]
    if len(argv) < 1:
        raise ValueError("please specify path to the input file")

    file = argv[0]
    with open(file) as f:
        all = f.read()
        lines = all.splitlines()
        for url in lines:
            html = render(url)
            start = time.monotonic_ns()
            soup = bs4.BeautifulSoup(html, 'html.parser')
            print(f"BS4 parsed '{url}' ({(time.monotonic_ns() - start) / 1e9:.3}s)")

            hrefs = []
            for a in soup.find_all('a', attrs={"data-fancybox" : "gallery"}):
                h = a.get('href')
                print(h)
                hrefs.append(h)


            for h in hrefs:
                if not h: continue

                r = h.rfind("-")
                if r > -1:
                    filename: str = h[r+1:]
                    filename = filename.replace("/", "-")
                else:
                    r = h.rfind("/")
                    filename = h[r+1:]

                if os.path.exists(filename): 
                    print(f"'{h}' already downloaded as '{filename}'")

                try:
                    with open(filename, "wb") as df:
                        start = time.monotonic_ns()
                        response = session.get(h, timeout=20)
                        df.write(response.content)
                        print(f"Downloaded '{h}' as '{filename}' ({(time.monotonic_ns() - start) / 1e9:.3}s)")
                except Exception as e:
                    print(f"Failed to download '{h}', error: {e}")