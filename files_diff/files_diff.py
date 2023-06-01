import os
import sys
import argparse


def list_files(path):
    dict = {}
    for (dir_path, dir_names, file_names) in os.walk(path):
        for i in range(len(file_names)):
            abspath = dir_path + "/" + file_names[i]
            dict[file_names[i]] = {
                "abspath": abspath,
                "size": os.stat(abspath).st_size,
            }
    return dict


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--fromdir", help="from dir", required=True, type=str)
    ap.add_argument("--todir", help="to dir", required=True, type=str)
    ap.add_argument("--move-to", help="move non existing file to", required=False, type=str)
    args = ap.parse_args(sys.argv[1:])

    ff = list_files(args.fromdir)
    tf = list_files(args.todir)

    for p, ap in ff.items():
        if p in tf and ap['size'] == tf[p]['size']:
            print(f"'{ap['abspath']}' in '{args.todir}' as '{tf[p]['abspath']}' (size: {ap['size']})")
            if args.moveto:
                os.rename(ap['abspath'], f'{args.moveto}/{p}')
                print(f"Moved '{ap['abspath']}' to f'{args.moveto}/{p}'")
