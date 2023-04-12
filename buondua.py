import os
import sys
import time
import requests
import argparse
import bs4
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import requests_html
import urllib.parse

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


'''
pip install beautifulsoup4
pip install requests_html

For buondua.com

Yongj.zhuang
'''
# proxy_server = 'socks5://127.0.0.1:7891'
proxies = {
   'http': 'http://localhost:7890',
   'https': 'http://localhost:7890',
}

mock = False 
render_timeout=10
render_request_timeout = 5 
download_timeout = 10
show_stat = False 
seg = ['mrcong.com', 'buondua.art', 'buondua.com']
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
PRE_PROCESSED_LINE = "--- PRE_PROCESSED (Website) ---"
PARSED_LINE = "--- PARSED (Website) ---"
EXTRACTED_LINE = "--- EXTRACTED (Image) ---"
DOWNLOADED_LINE = "--- DOWNLOADED (Image) ---"
END_LINE = "--- END ---"

STAGE_PRISTINE = 0
STAGE_PREPROCESSED = 1
STAGE_PARSED = 2
STAGE_EXTRACTED = 3
STAGE_DOWNLOAED = 4

session = HTMLSession()

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
        if site in self.pristine:
            self.pristine.remove(site)
        self.preprocessed.add(site)

    def rec_parsed(self, site: str):
        if site in self.preprocessed:
            self.preprocessed.remove(site)
        self.parsed.add(site)
        
    def rec_extracted(self, img_urls: list[str]):
        for u in img_urls: 
            self.extracted.add(u)

    def rec_downloaded(self, img_url: str):
        if img_url in self.extracted:
            self.extracted.remove(img_url)
        self.downloaded.add(img_url)
    
    def persist(self): 
        content = "# Please enter website urls below:\n\n"

        if self.pristine:
            content += "\n".join(self.pristine) + "\n"
        content += PRE_PROCESSED_LINE

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
                    self.preprocessed = curr
                elif stage == STAGE_PARSED:
                    self.parsed = curr
                elif stage == STAGE_EXTRACTED:
                    self.extracted = curr
                elif stage == STAGE_DOWNLOAED:
                    self.downloaded = curr            

    def is_finished(self) -> bool:
        return len(self.pristine) < 1 \
            and len(self.preprocessed) < 1 \
            and len(self.parsed) < 1 \
            and len(self.extracted) < 1


def render_html(url: str) -> str:
    # session = HTMLSession(browser_args=[f"--proxy-server={proxy_server}"])
    # r = session.get(url, timeout=render_timeout, proxies=proxies)

    start = time.time()
    r = session.get(url, timeout=render_request_timeout, stream=True)
    html: requests_html.HTML = r.html
    if show_stat: print(f"Fetched HTML '{url}' (took {(time.time() - start):.3}s)")

    start = time.time()
    html.render(retries=10, timeout=render_timeout, wait=2)
    if show_stat: print(f"Rendered HTML '{url}' (took {(time.time() - start):.3}s)")

    return html.html


def filter_img_url(url: str) -> bool:
    if not url: return False
    for s in seg:
        if url.find(s) > -1: return True
    return False


def parse_pagination(url) -> list[str]:
    html = render_html(url) 
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
    print(">>> Start extracting image urls from websites ...")

    preprocessed = set(ctx.preprocessed)
    total = len(preprocessed)
    i = 0
    for url in preprocessed: 
        i += 1
        progress = f"[{i}/{total}]"

        # print(f"Fetching HTML for '{url}'")
        try:
            decoded_url = urllib.parse.unquote(url)
            html = render_html(url) 

            extracted = []
            soup = BeautifulSoup(html, 'html.parser')
            for img in soup.find_all('img'):
                src: str = img.get('src')

                if not filter_img_url(src): continue
                extracted.append(src)
            print(f"{progress} Parsed '{decoded_url}', found {len(extracted)} image urls")

            if not extracted:
                raise AssertionError(f"Found no image in '{decoded_url}'")

            ctx.rec_extracted(extracted)
            ctx.rec_parsed(url)
        except ConnectionError: return
        except Exception as e:
            print(f"{progress} Failed to parse url '{decoded_url}'", e)


suf = ['.webp', '.jpg', '.jpeg', '.png']
def extract_name(url: str) -> str:
    i = url.rfind('?')
    if i > -1: url = url[:i]

    urllower = url.lower()
    for s in suf:
        j = urllower.rfind(s)
        if j < 0: continue

        i = url.rfind('/', 0, j)
        return url[i+1:j+len(s)] 

    raise ValueError(f'Failed to extract filename for "{url}"')


def download(ctx: Context, target_dir: str):
    print(">>> Start downloading ...")

    extracted: set[str] = set(ctx.extracted)
    total = len(extracted)
    i = 0

    for img_url in extracted: 
        i += 1
        filename = target_dir + extract_name(img_url)
        progress = f"[{i}/{total}]"

        if os.path.exists(filename): 
            ctx.rec_downloaded(img_url)
            print(f"{progress} File '{filename}' already downloaded")
            continue

        try:
            if mock:
                print(f"{progress} Downloaded (mocked) '{img_url}' as '{filename}'")
            else:
                response = requests.get(img_url, timeout=download_timeout)
                with open(filename, "wb") as df:
                    df.write(response.content)
                print(f"{progress} Downloaded '{img_url}' as '{filename}'")
            
            ctx.rec_downloaded(img_url)
        except ConnectionError: return
        except Exception as e:
            print(f"{progress} Failed to download '{img_url}'", e)
    

def load_sites(file: str) -> list[str]:
    with open(file, "r") as f:
        mapped = map(lambda x: x.replace("\n", ""), f.readlines())
        filtered = filter(lambda x : x and not x.startswith("#"), mapped)
        return list(filtered)


def write_sites(file: str, sites: list[str]):
    with open(file, "w") as f:
        f.write("\n".join(sites))


def preprocess_sites(ctx : Context):
    print(">>> Start pre-processing ....")

    remaining = set(ctx.pristine)
    total = len(remaining)
    i = 0
    for site in remaining:
        i += 1
        decoded_site = urllib.parse.unquote(site)
        progress = f"[{i}/{total}]"
        try:
            expanded = parse_pagination(site)
            for s in expanded:
                ctx.rec_preprocessed(s)
            print(f"{progress} Pre-processed '{decoded_site}'")
        except ConnectionError: return
        except Exception as e: 
            print(f"{progress} Failed to parse pagination for '{decoded_site}'", e)

def buondua():
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
        return

    context = Context(inputf)
    context.load()
    
    if context.is_finished():
        print(f"Download is finished, remove '{inputf}' for another fresh download")
        return

    preprocess_sites(context)
    context.persist()
    if len(context.pristine) > 0:
        print(f"Failed to preprocess all websites, please try again")
        return

    extract_img_urls(context)
    context.persist()
    if len(context.preprocessed) > 0:
        print(f"Failed to parse all websites, please try again")
        return

    download(context, dir)
    context.persist()
    if len(context.extracted) > 0:
        print(f"Failed to download all images, please try again")
        return

    context.persist()
    print(f"Download is finished, remove '{inputf}' for another fresh download")


if __name__ == "__main__":
    buondua()
