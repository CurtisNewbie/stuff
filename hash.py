import argparse
import base64
from operator import mod
import sys
from Crypto.Hash import SHA256, SHA1, MD5, SHA512

DESC = '''
hash.py by Yongj.Zhuang

powered by pycryptodome

By default it uses SHA256
'''
MODES = ['sha256', 'sha1', 'md5']
MODES_MODULE = {'sha256': SHA256, 'sha1': SHA1, 'md5': MD5, 'sha512': SHA512}


def resolvemod(mode: str):
    lm = mode.lower()
    mod = MODES_MODULE.get(lm, None)
    if mod is None:
        print(f"Mode '{lm}' is not supported, only {MODES}\n")
        sys.exit(1)
    return mod


'''
hash.py by Yongj.Zhuang

pip install pycryptodome
'''
if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=DESC, formatter_class=argparse.RawTextHelpFormatter)

    ap.add_argument('-m', '--mode', type=str, help=f"hashing mode, {MODES}", default='sha256')
    ap.add_argument('-c', '--content', type=str, help=f"content (for multi-line content, do not specify this argument)", default='')
    args = ap.parse_args()
    ms = args.mode

    mod = resolvemod(ms)
    print(f"\nUsing Algorithm: {ms.upper()}\n")

    ctn = args.content
    if not ctn:
        print("Please enter the data that you want to hash: (Press again 'Enter' to finish)")
        lines = []
        while True:
            line = input()
            if line: lines.append(line)
            else: break
        ctn = '\n'.join(lines)

    if not ctn:
        print("Have nothing to hash, aborting...\n")
        sys.exit(0)

    newm = getattr(mod, "new")
    hashobj = newm(data=ctn.encode('utf-8'))

    print(base64.urlsafe_b64encode(hashobj.digest()).decode('utf-8'))
    print()
