import subprocess
import re
import datetime

'''
https://go.dev/ref/mod#glos-pseudo-version

git log head -1

commit 6a076566e74140197fb1c1c5f8f3dc5ef8d504d0 (HEAD -> dev, origin/dev)
Author: yongj.zhuang <yongj.zhuang@outlook.com>
Date:   Tue Sep 26 16:30:30 2023 +0800

    Handle error properly

'''

pipe = True
tag = None

with subprocess.Popen(f"git tag --sort=-creatordate", shell=True, stdout=subprocess.PIPE) as p:
    std = str(p.stdout.read(), 'utf-8')

    sl = std.splitlines()
    for l in sl:
        if not l:
            continue

        tag = l.strip()
        break

    #print(f"Tag: {tag}")

if not tag:
    tag = "v0.0.0"
else:
    if re.match("^v\d+\.\d+\.\d+\-\w+\.\d$", tag):
        tag = tag + ".0"


with subprocess.Popen(f"git log head -1", shell=True, stdout=subprocess.PIPE) as p:
    std = str(p.stdout.read(), 'utf-8')

    sl = std.splitlines()
    if len(sl) < 1:
        exit(0)

    commit = ""
    date = ""
    for l in sl:
        m = re.match('^commit (\w+) *.*$', l)
        if m:
            commit = m[1]
            continue

        m = re.match('^Date: +(.*)$', l)
        if m:
            date = m[1]
            continue

    if not pipe:
        print(f"Commit: {commit}")
        print(f"Date: {date}")

    parsed = datetime.datetime.strptime(date, '%a %b %d %H:%M:%S %Y %z')
    ts = parsed.astimezone(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')
    if not pipe:
        print(f"TS: {ts}")

    pver = tag + '.' + ts + '-' + commit[0:12]
    if not pipe:
        print(f"Persudo Version: {pver}")
        print(f"\n\t{pver}")
        print()

    if pipe:
        print(pver)
