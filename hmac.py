import argparse
import sys
from Crypto.Hash import SHA256, SHA1, MD5, SHA512, HMAC

DESC = '''
hmac.py by Yongj.Zhuang

powered by pycryptodome

By default it uses HMAC-SHA256
'''
MODES = ['sha256', 'sha1', 'md5']
MODES_MODULE = {'sha256': SHA256,
                'sha1': SHA1, 'md5': MD5, 'sha512': SHA512}


def resolvemod(mode: str):
    lm = mode.lower()
    mod = MODES_MODULE.get(lm, None)
    if mod is None:
        print(f"Mode '{lm}' is not supported, only {MODES}\n")
        sys.exit(1)
    return mod


'''
hmac.py by Yongj.Zhuang

pip install pycryptodome
'''
if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description=DESC, formatter_class=argparse.RawTextHelpFormatter)

    ap.add_argument('-m', '--mode', type=str,
                          help=f"hashing mode, {MODES}", default='sha256')
    ap.add_argument('-s', '--secret', type=str,
                          help=f"hmac secret", required=True)
    ap.add_argument('-c', '--content', type=str,
                          help=f"content to be signed", required=True)
    args = ap.parse_args()
    ms = args.mode

    resolved = resolvemod(ms)
    print(f"\nUsing Algorithm: {ms.upper()}\n")

    secret = str.encode(args.secret)
    h = HMAC.new(secret, digestmod=resolved)
    h.update(str.encode(args.content))
    print(h.hexdigest()) 
    print()
