import argparse as argp
from base64 import b64decode, b64encode
import getpass
import sys
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

ENCRYPT_MODE = 'encrypt'
DECRYPT_MODE = 'decrypt'

DESC = '''
aes.py by Yongj.Zhuang

This tool use AES256 + CBC Mode for encryption/decryption

When encrypting data, a random 16 bytes initialization vector is generated and inserted into the begining of the cipher text
if you want to decrypt the data with other tools, be sure to extract the 16 bytes IV first
'''

REQUIRED_KEY_LENGTH = int(256 / 8)


def padzero(key: str, requiredlen: int = REQUIRED_KEY_LENGTH) -> bytes:
    arr: bytearray = bytearray(key, 'utf-8')
    al = len(arr)
    if al > requiredlen:
        raise ValueError(f'Key can be at most {requiredlen} bytes long')

    remaining = requiredlen - al
    if remaining > 0:
        for i in range(remaining):
            arr.append(0)
    return bytes(arr)


def geniv() -> bytes:
    return get_random_bytes(16)


def argparser() -> argp.ArgumentParser:

    ap = argp.ArgumentParser(
        description=DESC, formatter_class=argp.RawTextHelpFormatter)
    required = ap.add_argument_group('required arguments')
    required.add_argument('-m', '--mode', type=str,
                          help=f"encrypt/decrypt Mode, either '{ENCRYPT_MODE}' or '{DECRYPT_MODE}'", required=True)
    return ap


def is_legal_mode(mode: str) -> bool:
    ml = mode.lower()
    return ml == ENCRYPT_MODE or ml == DECRYPT_MODE


'''
aes.py by Yongj.Zhuang

pip install pycryptodome
'''
if __name__ == '__main__':
    parser: argp.ArgumentParser = argparser()
    args: argp.Namespace = parser.parse_args()

    mode = args.mode
    if not is_legal_mode(mode):
        print(
            f"mode value illegal, it should be either '{ENCRYPT_MODE}' or '{DECRYPT_MODE}'")
        sys.exit(1)

    isencrypt = mode.lower() == ENCRYPT_MODE
    print("Please enter the data that you want to encrypt/decrypt: (Press again 'Enter' to finish)")
    if isencrypt:
        lines = []
        while True:
            line = input()
            if line:
                lines.append(line)
            else:
                break
        data = '\n'.join(lines)
    else:
        data = input()

    if not data:
        print("Have nothing to " + ("encrypt" if isencrypt else "decrypt"))
        sys.exit(0)

    password = getpass.getpass("Please provide your password:")

    if isencrypt:
        cipher = AES.new(key=padzero(password), mode=AES.MODE_CBC)
        bdata = data.encode('utf-8')
        ctbytes = cipher.encrypt(pad(bdata, AES.block_size))
        iva = bytearray(cipher.iv)
        cta = bytearray(ctbytes)
        for i in range(len(cta)):
            iva.append(cta[i])

        print(b64encode(iva).decode('utf-8'))
    else:
        decoded: bytes = b64decode(data)
        darray = bytearray(decoded)

        # iv is the first 16 bytes
        biv: bytearray = darray[:16]
        cipher = AES.new(key=padzero(password),
                         mode=AES.MODE_CBC, iv=biv)

        ct: bytearray = darray[16:]
        pt: bytes = unpad(cipher.decrypt(ct), AES.block_size)
        print(pt.decode('utf-8'))
