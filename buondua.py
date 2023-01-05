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

mock = False
render_timeout = 60
down_timeout = 10
seg = ['kul.mrcong.com', 'buondua.art']
base = 'https://buondua.com'

'''
Format of the input file:

[sites that haven't been pre-processed]
[sites that haven't been pre-processed]
[sites that haven't been pre-processed]

--- PRE_PROCESSED ---

[sites that have been pre-processed]
[sites that have been pre-processed]
[sites that have been pre-processed]

--- PARSED ---

[sites that have been parsed]
[sites that have been parsed]
[sites that have been parsed]

--- EXTRACTED ---

[img urls extracted]
[img urls extracted]
[img urls extracted]

--- DOWNLOADED ---

[img urls downloaded]
[img urls downloaded]
[img urls downloaded]

--- END ---

'''
PRE_PROCESSED_LINE = "--- PRE_PROCESSED ---"
PARSED_LINE = "--- PARSED ---"
EXTRACTED_LINE = "--- EXTRACTED ---"
DOWNLOADED_LINE = "--- DOWNLOADED ---"
END_LINE = "--- END ---"

STAGE_PRISTINE = 0
STAGE_PREPROCESSED = 1
STAGE_PARSED = 2
STAGE_EXTRACTED = 3
STAGE_DOWNLOAED = 4

class Context:
    
    def __init__(self, file: str):
        self.file = file
        # self._reset()

    def _reset(self):
        self.pristine = set() # website url
        self.preprocessed = set() # website url
        self.parsed = set()  # website url
        self.extracted = set() # image url
        self.downloaded = set() # image url

    def __str__(self):
        s = "Context:"
        s += f'\n - pristine (website): {self.pristine if hasattr(self, "pristine") else "nil"}'
        s += f'\n - preprocessed (website): {self.preprocessed if hasattr(self, "preprocessed") else "nil"}'
        s += f'\n - parsed (website): {self.parsed if hasattr(self, "parsed") else "nil"}'
        s += f'\n - extracted (image): {self.extracted if hasattr(self, "extracted") else "nil"}'
        s += f'\n - downloaded (image): {self.downloaded if hasattr(self, "downloaded") else "nil"}'
        return s

    def rec_preprocessed(self, site: str):
        self.pristine.remove(site)
        self.preprocessed.add(site)

    def rec_parsed(self, site: str):
        self.preprocessed.remove(site)
        self.parsed.add(site)
        
    def rec_extracted(self, img_urls: list[str]):
        for u in img_urls: 
            self.extracted.add(u)

    def rec_downloaded(self, img_url: str):
        self.extracted.remove(img_url)
        self.downloaded.add(img_url)
    
    def persist(self): 
        content = ""

        if self.pristine:
            content += "\n" + "\n".join(self.pristine)
        content += "\n" + PRE_PROCESSED_LINE

        if self.preprocessed:
            content += "\n" + "\n".join(self.preprocessed)
        content += "\n" + PARSED_LINE 

        if self.parsed:
            content += "\n" + "\n".join(self.parsed)
        content += "\n" + EXTRACTED_LINE 

        if self.extracted:
            content += "\n" + "\n".join(self.extracted)
        content += "\n" + DOWNLOADED_LINE 

        if self.downloaded:
            content += "\n" + "\n".join(self.downloaded)
        content += "\n" + END_LINE 

        with open(self.file, "w") as f:
            f.write(content)


    def load(self):
        self._reset()

        with open(self.file, "r") as f:
            lines = list(filter(lambda l: l and not l.startswith("#"), map(lambda x: x.replace("\n", "").strip(), f.readlines())))

            reset_curr = False
            curr = set() 
            stage = STAGE_PRISTINE 

            for l in lines:
                if l == PRE_PROCESSED_LINE:
                    reset_curr = True
                    self.pristine = curr
                elif l == PARSED_LINE:
                    reset_curr = True
                    self.preprocessed = curr
                elif l == EXTRACTED_LINE:
                    reset_curr = True
                    self.parsed = curr
                elif l == DOWNLOADED_LINE: 
                    reset_curr = True
                    self.extracted = curr
                elif l == END_LINE: 
                    reset_curr = True
                    self.downloaded = curr
                else:
                    curr.add(l)
                
                if reset_curr:
                    reset_curr = False
                    curr = set()
                    stage = stage + 1

                    if stage > STAGE_DOWNLOAED + 1:
                        break

            if len(curr) > 0:
                if stage == STAGE_PRISTINE:
                    self.pristine = curr
                elif stage == STAGE_PREPROCESSED:
                    self.preprocessing = curr
                elif stage == STAGE_PARSED:
                    self.parsed = curr
                elif stage == STAGE_EXTRACTED:
                    self.extracted = curr
                elif stage == STAGE_DOWNLOAED:
                    self.downloaded = curr            

    def is_finished(self) -> bool:
        if len(self.pristine) > 0 or len(self.preprocessed) > 0:
            return False 
        if len(self.parsed) > 0 or len(self.extracted) > 0:
            return False
        return True 

def render_html(url: str) -> str:
    # session = HTMLSession(browser_args=[f"--proxy-server={proxy_server}"])
    # r = session.get(url, timeout=render_timeout, proxies=proxies)

    session = HTMLSession()
    r = session.get(url, timeout=render_timeout)
    r.html.render()
    return r.html.html


def filter_img_url(url: str) -> bool:
    for s in seg:
        if url.find(s) > -1: return True
    return False


def parse_pagination(url) -> list[str]:
    renderstart = time.time()
    html = render_html(url) 
    print(f"Rendered HTML '{url}' (took {(time.time() - renderstart):.3}s)")

    expanded = [url]
    soup = BeautifulSoup(html, 'html.parser')
    
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
            if not isinstance(pspan, bs4.element.Tag):
                continue
            for atag in pspan.descendants:
                if not isinstance(atag, bs4.element.Tag):
                    continue
                href = atag.get('href')
                if not href: 
                    continue
                if not href.lower().startswith('http'): 
                    href = base + "/" + urllib.parse.quote(href[1:], safe="")
                expanded.append(href)

    return expanded


def extract_img_urls(ctx: Context): 
    print("Start extracting image urls from websites ...")

    preprocessed = set(ctx.preprocessed)
    total = len(preprocessed)
    i = 0
    for url in preprocessed: 
        i += 1
        progress = f"[{i+1}/{total}]"

        print(f"Fetching HTML for '{url}'")
        try:
            renderstart = time.time()
            html = render_html(url) 
            print(f"Rendered HTML '{url}' (took {(time.time() - renderstart):.3}s)")

            extracted = []
            soup = BeautifulSoup(html, 'html.parser')
            for img in soup.find_all('img'):
                src: str = img.get('src')

                if not filter_img_url(src): continue
                extracted.append(src)
            print(f"{progress} Parsed '{url}', found {len(extracted)} image urls")

            ctx.rec_extracted(extracted)
            ctx.rec_parsed()

        except Exception as e:
            print(f"{progress} Failed to parse url '{url}': {e}")


suf = ['.webp', '.jpg', '.jpeg']
def extract_name(url: str) -> str:
    i = url.rfind('?')
    if i > -1: url = url[:i]

    for s in suf:
        j = url.rfind(s)
        if j < 0: continue

        i = url.rfind('/', 0, j)
        return url[i+1:j+len(s)] 

    raise ValueError(f'Failed to extract filename for "{url}"')


def download(ctx: Context, target_dir: str):
    print("Start downloading ...")

    extracted: set[str] = set(ctx.extracted)
    total = len(extracted)
    i = 0

    for img_url in extracted: 
        i += 1
        filename = target_dir + extract_name(img_url)
        progress = f"[{i}/{total}]"

        if os.path.exists(filename): 
            print(f"{progress} File '{filename}' already downloaded")
            continue

        try:
            if mock:
                print(f"{progress} Downloaded (mocked) '{img_url}' as '{filename}'")
            else:
                response = requests.get(img_url, timeout=down_timeout)
                with open(filename, "wb") as df:
                    df.write(response.content)
                print(f"{progress} Downloaded '{img_url}' as '{filename}'")
            
            ctx.rec_downloaded(img_url)
        except Exception as e:
            print(f"{progress} Failed to download '{img_url}': {e}")
    

def load_sites(file: str) -> list[str]:
    with open(file, "r") as f:
        mapped = map(lambda x: x.replace("\n", ""), f.readlines())
        filtered = filter(lambda x : x and not x.startswith("#"), mapped)
        return list(filtered)


def write_sites(file: str, sites: list[str]):
    with open(file, "w") as f:
        f.write("\n".join(sites))


def preprocess_sites(ctx : Context):
    if not ctx.pristine:
        return

    remaining = set(ctx.pristine)
    for site in remaining:
        try:
            expanded = parse_pagination(site)
            for s in expanded:
                ctx.rec_preprocessed(s)
        except Exception as e: 
            print(f"Failed to parse pagination for '{site}', e: {e}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(epilog="python3 buondua.py  -d '/my/folder' -m 'all' -f 'download_url.txt'",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-d", "--dir", help="Download directory, by default it's current directory", required=False, default="./")
    ap.add_argument("-f", "--file", help="Input file with all the website urls, this argument is optional. By default it looks for 'download_url.txt'", required=False, default="download_url.txt")

    args = ap.parse_args()
    dir = args.dir if args.dir.endswith("/") else args.dir + "/"

    inputf = args.file

    if not os.path.exists(inputf):
        with open(inputf, "a") as f:
            f.write("# Please enter website urls below:\n")
        print(f"Please provide website urls in '{inputf}'")
        sys.exit(0)

    context = Context(inputf)
    context.load()
    # print(f"Loaded context: \n{context}")
    
    if context.is_finished():
        print(f"Download is finished, remove '{inputf}' for another fresh download")
        sys.exit(0)

    preprocess_sites(context)
    if len(context.pristine) > 0:
        context.persist()
        print(f"Failed to preprocess all websites, please try again")
        sys.exit(0)

    extract_img_urls(context)
    if len(context.preprocessed) > 0:
        context.persist()
        print(f"Failed to parse all websites, please try again")
        sys.exit(0)

    download(context, dir)
    if len(context.extracted) > 0:
        context.persist()
        print(f"Failed to download all images, please try again")
        sys.exit(0)

    context.persist()
    print(f"Download is finished, remove '{inputf}' for another fresh download")

