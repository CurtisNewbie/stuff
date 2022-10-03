import sys


def split(text, delimiter):
    arr = text.split(delimiter)
    for v in arr:
        s = v.strip()
        if s != '':
            print(s)


def print_help():
    print('arg[0] - text to be splited')
    print('arg[1] - delimiter')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()

    text = sys.argv[1]
    if len(sys.argv) > 2:
        delimiter = sys.argv[2]
    else:
        delimiter = ','

    split(text, delimiter)
