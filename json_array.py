import sys


def json_arr(text):
    arr = text.split(",")
    joined = '['

    for i, v in enumerate(arr):
        if i > 0:
            joined += ',';
        joined += '"' + v.strip() + '"'

    joined += ']'
    print(joined)


def print_help():
    print('arg[0] - comma delimited strings to be joined as a json array')

if __name__ == "__main__"   :
    if len(sys.argv) < 2: 
        print_help()
        raise Exception('Illegal Arguments')

    json_arr(sys.argv[1])
