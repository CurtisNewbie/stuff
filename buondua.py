import os
import sys
import time
import requests
import argparse
from bs4 import BeautifulSoup
from requests_html import HTMLSession

'''
pip install beautifulsoup4
pip install requests_html

For buondua.com

Yongj.zhuang
'''

render_timeout = 60
down_timeout = 10
seg = ['kul.mrcong.com', 'buondua.art']


def render_html(url: str) -> str:
    session = HTMLSession()
    r = session.get(url, timeout=render_timeout)
    r.html.render(timeout=render_timeout)
    return r.html.html


def filter_url(url: str) -> bool:
    for s in seg:
        if url.find(s) > -1: return True
    return False


def parse_urls(urls: list[str], output_file: str): 
    with open(output_file, "w") as f:
        t = len(urls)
        for i in range(t):
            url = urls[i] 
            print(f"Fetching html for '{url}'")

            retry = 5
            while True:
                try:
                    html = render_html(url) 
                    # print(html)

                    parsed = []
                    soup = BeautifulSoup(html, 'html.parser')
                    for img in soup.find_all('img'):
                        src: str = img.get('src')

                        if not filter_url(src): continue
                        parsed.append(src)

                    print(f"[{i+1}/{t}] Parsed '{url}', found: {len(parsed)}")
                    f.write(f"# [{i+1}/{t}] {url}, count: {len(parsed)}\n")
                    f.write("\n".join(parsed) + "\n\n")
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


def download(input_file: str, target_dir: str):
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
    else:
        print(f"Successfully downloaded {dcnt} files")
        os.remove(input_file)
    

def load_sites(file: str) -> list[str]:
    with open(file, "r") as f:
        mapped = map(lambda x: x.replace("\n", ""), f.readlines())
        filtered = filter(lambda x : x and not x.startswith("#"), mapped)
        return list(filtered)


if __name__ == "__main__":
    parsed = 'parse_url.txt'
    ap = argparse.ArgumentParser(epilog="python3 buondua.py  -d '/my/folder' -m 'all' -f 'download_url.txt'",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-d", "--dir", help="Download directory", required=True)
    ap.add_argument("-f", "--file", help="Input file with all the website urls, by default it looks for 'download_url.txt'", required=False, default="download_url.txt")

    args = ap.parse_args()
    dir = args.dir if args.dir.endswith("/") else args.dir + "/"

    if not os.path.exists(parsed): 
        inputf = args.file
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

    download(parsed, dir)