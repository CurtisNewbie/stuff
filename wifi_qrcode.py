import qrcode
from typing import *
from util import *

# Flags that indicate a feature or a switch is turned on when they present
HELP_FLAG: str = '--help'
# Set of flag keys
flag_set: Set[str] = {HELP_FLAG}

# Argument keys
SIZE_ARG = "-s"
OUTPUT_ARG = "-o"
WIFI_PWD_ARG = "-p"
WIFI_NAME_ARG = "-n"

# def size
DEF_SIZE = 10


def print_help() -> None:
    """
    Print help
    """
    print(f"\n  wifi_qrcode.py by yongj.zhuang\n")
    print(f"  Arguments:\n")
    print(f"{TT}{SIZE_ARG}{T}size of the QRCode (from 1 to 40)")
    print(f"{TT}{OUTPUT_ARG}{T}path to the output QRCode image")
    print(f"{TT}{WIFI_NAME_ARG}{T}wifi name")
    print(f"{TT}{WIFI_PWD_ARG}{T}wifi password\n")
    print(f"  E.g., \n")
    print(f"{TT}{WIFI_NAME_ARG} 'mywifi' {WIFI_PWD_ARG} 'mypassword' {SIZE_ARG} 10 {OUTPUT_ARG} wifi.png\n")


def prep_wifi_code(ctx: "Context") -> str:
    """
    Prep code for WIFI

    :param ctx context
    """
    assert_true(ctx.is_present(WIFI_NAME_ARG), f"{WIFI_NAME_ARG} must be specified")
    assert_true(ctx.is_present(WIFI_PWD_ARG), f"{WIFI_PWD_ARG} must be specified")
    name = ctx.get_first(WIFI_NAME_ARG)
    pwd = ctx.get_first(WIFI_PWD_ARG)
    return f"WIFI:T:WPA;S:{name};P:{pwd};;"


def gen_qrcode(content: str, size: int, path: str) -> None:
    """
    Generate QRCode

    :param content: content to be encoded
    :param path: output path
    """

    qr = qrcode.QRCode(version=size)
    qr.add_data(content)
    img = qr.make_image()
    img.save(path)

"""
WIFI QRCode Generator

    pip install qrcode[pil]

yongj.zhuang
"""

if __name__ == '__main__':
    args = sys.argv[1:]

    # no arg provided
    if len(args) == 0:
        print_help()
        sys.exit(0)

    # parse args as context
    ctx = Context(args, lambda x: x in flag_set)
    if ctx.is_present(HELP_FLAG):
        print_help()
        sys.exit(0)

    # version / size
    s = ctx.get_first(SIZE_ARG) if ctx.is_present(SIZE_ARG) else DEF_SIZE
    assert_true(0 < s <= 40, "Size must be between 1 and 40")

    # prepare wifi code
    wifi_code = prep_wifi_code(ctx)

    # path
    assert_true(ctx.is_present(OUTPUT_ARG), f"{OUTPUT_ARG} argument is missing")
    p = ctx.get_first(OUTPUT_ARG)

    # generate qrcode
    gen_qrcode(wifi_code, s, p)
