import os
import sys
import argparse
import random
import string

THRESHOLD = 15

def list_files(path):
    d = {}
    for (dir_path, dir_names, file_names) in os.walk(path):
        for i in range(len(file_names)):
            abspath = dir_path + "/" + file_names[i]
            d[file_names[i]] = {
                "abspath": abspath,
                "name": file_names[i]
            }
    return d


def randomize(name: str):
    i = name.rfind(".")
    ext = ""
    if i > 0:
        ext = name[i+1:]
        name = name[:i]

    s = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(15))
    if ext: s = s + "." + ext
    return s

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputdir", help="input dir", required=True, type=str)
    ap.add_argument("--apply", help="apply the change", action="store_true")
    args = ap.parse_args(sys.argv[1:])

    ff = list_files(args.inputdir)
    for k, v in ff.items():
        if len(v['name']) > THRESHOLD:
            continue

        fr = v['abspath']
        name = v['name']
        to = f'{args.inputdir}/{randomize(name)}'

        if args.apply:
            os.rename(fr, to)
            print(f"Moved '{fr}' to '{to}'")
        else:
            print(f"Will moved '{fr}' to '{to}'")
