import random
import sys

DEFAULT_LEN = 25


def buildcharset() -> str:
    s = ""
    for i in range(26):
        s = s + chr(i + ord('a'))
        s = s + chr(i + ord('A'))

    for i in range(10):
        s = s + chr(i + ord('0'))
    return s


if __name__ == '__main__':
    letters = buildcharset()
    length = DEFAULT_LEN 

    if len(sys.argv) > 1: 
        length = int(sys.argv[1])
        
    print(''.join(random.choice(letters) for i in range(length)))
