import os
import sys
import time
import requests
import argparse
import bs4
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import urllib.parse

'''
pip install beautifulsoup4
pip install requests_html

For buondua.com

Yongj.zhuang
'''
# proxy_server = 'socks5://127.0.0.1:7891'
# proxies = {
#    'http': 'http://localhost:7890',
#    'https': 'http://localhost:7890',
# }


max_retry = 5 
render_timeout = 60
down_timeout = 10
seg = ['kul.mrcong.com', 'buondua.art']
base = 'https://buondua.com'
parsed = 'parse_url.txt'


def render_html(url: str) -> str:
    # session = HTMLSession(browser_args=[f"--proxy-server={proxy_server}"])
    # r = session.get(url, timeout=render_timeout, proxies=proxies)

    session = HTMLSession()
    r = session.get(url, timeout=render_timeout)
    r.html.render()
    return r.html.html


def filter_url(url: str) -> bool:
    for s in seg:
        if url.find(s) > -1: return True
    return False


def parse_urls(urls: list[str], output_file: str): 
    parsed = set()

    with open(output_file, "w") as f:
        i = 0
        while i < len(urls):
            url = urls[i] 
            if url in parsed:
                i = i + 1
                continue

            print(f"Fetching HTML for '{url}'")
            t = len(urls)

            retry = max_retry
            while True:
                try:
                    renderstart = time.time()
                    html = render_html(url) 
                    print(f"Rendered HTML '{url}' (took {(time.time() - renderstart):.3}s)")
                    # print(html)

                    extracted = []
                    soup = BeautifulSoup(html, 'html.parser')
                    for img in soup.find_all('img'):
                        src: str = img.get('src')

                        if not filter_url(src): continue
                        extracted.append(src)
                    
                    # it may have several pages (div -> span -> a.href) 
                    '''
                    <nav class="pagination">
                        <div class="pagination-list">
                            <span> <a class="pagination-link is-current" href="..."> 1 </a> </span>
                            <span> <a class="pagination-link " href="..."> 2 </a> </span>
                        </div>
                    </nav>
                    '''

                    for pdiv in soup.find_all('div', {"class": "pagination-list"}):
                        for pspan in pdiv.descendants:
                            if isinstance(pspan, bs4.element.Tag):
                                for atag in pspan.descendants:
                                    if isinstance(atag, bs4.element.Tag):
                                        href = atag.get('href')
                                        if not href: continue
                                        if not href.lower().startswith('http'): 
                                            href = base + "/" + urllib.parse.quote(href[1:], safe="")
                                        if href not in urls: urls.append(href)

                    print(f"[{i+1}/{t}] Parsed '{url}', found: {len(extracted)}")
                    f.write(f"# [{i+1}/{t}] {url}, count: {len(extracted)}\n")
                    f.write("\n".join(extracted) + "\n\n")

                    i = i + 1
                    parsed.add(url)
                    break 
                except Exception as e:
                    retry = retry - 1
                    print(f"[{i+1}/{t}] Failed to parse url '{url}', e: {e}, retry remaining: {retry}")
                    if retry == 0:
                        raise e
                    time.sleep(1)


suf = ['.webp', '.jpg', '.jpeg']
def extract_name(url: str) -> str:
    i = url.rfind('?')
    if i > -1: url = url[:i]

    for s in suf:
        j = url.rfind(s)
        if j < 0: continue

        i = url.rfind('/', 0, j)
        # print(f"url: {url}, i: {i}, j: {j}")
        return url[i+1:j+len(s)] 

    raise ValueError(f'Failed to extract filename for "{url}"')


def download(input_file: str, target_dir: str) -> bool:
    print(f"opening file: {input_file}\n")

    failed = []
    with open(input_file) as f:
        all = f.read().replace("\t", "\n")
        lines = all.splitlines()

        dcnt = 0
        t = len(lines)
        for i in range(t):
            url = lines[i]
            if not url: continue
            if url.startswith("#"): continue

            filename = target_dir + extract_name(url)
            if os.path.exists(filename): 
                print(f"[{i+1}/{t}] File '{filename}' already downloaded")
                continue
            dcnt = dcnt + 1

            try:
                response = requests.get(url, timeout=down_timeout)
                with open(filename, "wb") as df:
                    df.write(response.content)
                    print(f"[{i+1}/{t}] Downloaded '{url}' as '{filename}'")
            except Exception as e:
                failed.append(url)
                print(f"[{i+1}/{t}] Failed to download '{url}', error: {e}")

    if failed:
        remaining = "\n".join(failed)
        print(f"\nSome failed, please run again to download them: \n{remaining}")
        with open(input_file, "w") as f:
            f.write(remaining)
        return False
    else:
        os.remove(input_file)
        print(f"Successfully downloaded {dcnt} files, removed {input_file}")
        return True
    

def load_sites(file: str) -> list[str]:
    with open(file, "r") as f:
        mapped = map(lambda x: x.replace("\n", ""), f.readlines())
        filtered = filter(lambda x : x and not x.startswith("#"), mapped)
        return list(filtered)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(epilog="python3 buondua.py  -d '/my/folder' -m 'all' -f 'download_url.txt'",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-d", "--dir", help="Download directory, by default it's current directory", required=False, default="./")
    ap.add_argument("-f", "--file", help="Input file with all the website urls, by default it looks for 'download_url.txt'", required=False, default="download_url.txt")

    args = ap.parse_args()
    dir = args.dir if args.dir.endswith("/") else args.dir + "/"

    inputf = args.file
    if not os.path.exists(parsed): 
        if not os.path.exists(inputf):
            open(inputf, "a").close() # touch empty file
            print(f"Please provide website urls in {inputf}")
            sys.exit(0)

        sites = load_sites(inputf)
        # print(f"Loaded sites: {sites}")
        if not sites:
            print(f"Found no website urls in {inputf}")
            sys.exit(0)
        parse_urls(sites, parsed)

    if download(parsed, dir):
        os.remove(inputf)