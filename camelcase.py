import sys

uc_start = ord("A")
uc_end = ord("Z")
is_debug = False

def is_upper_case(s : str) -> bool:
    o = ord(s)
    return o >= uc_start and o <= uc_end


def camelcase(s : str) -> str:
    if not s: return s

    cc = ""
    for i in range(len(s)):
        si : str = s[i]
        if is_upper_case(si):
            if i > 0:
                si = "_" + si.lower()
            else:
                si = si.lower()

        cc = cc + si
    return cc


if __name__ == '__main__':
    args = sys.argv[1:]

    for i in range(len(args)):
        s = args[i]
        print(camelcase(s))




