from genericpath import exists
import io
import os
from pathlib import Path
import sys
from typing import Callable

isdebug = False


def lastc(s: str) -> str:
    c = s[len(s) - 1]
    return c


def dfs(parents: list[str], target: str):
    for i in range(len(parents)):
        root = parents[i]
        isdir = os.path.isdir(root)
        if isdir:
            entries: list[str] = os.listdir(root)
            for i in range(len(entries)):
                entries[i] = (root + "/" + entries[i]
                              ) if lastc(root) != "/" else (root + entries[i])
            dfs(entries, target)
        else:
            if matches(root, target):
                print(os.path.abspath(root))


def matches(curr: str, target: str) -> bool:
    rf = curr.rfind('/')
    pcurr = curr[rf+1:] if rf > -1 else curr
    ismatched = target in pcurr
    debug(
        lambda: f"matches, curr: '{curr}', target: '{target}', pcurr: '{pcurr}'")
    return ismatched


def debug(callback: Callable[[], str]):
    if isdebug:
        print("[debug] " + callback())


def printhelp():
    print("\npfind.py by Yongj.Zhuang\n")
    print("Please provide following arguments:\n")
    print("[0] - name of the file")
    print("[1] - where to find the file (optional)\n")


'''
pfind.py by Yongj.Zhuang

[0] - name of the file
[1] - where to find the file 
'''
if __name__ == '__main__':


    argv: list[str] = sys.argv
    debug(lambda: f"argv: {argv}")

    argv = argv[1:]
    nargv = len(argv)
    if nargv < 1:
        printhelp()
        sys.exit(1)

    target = argv[0]
    root = argv[1] if nargv > 1 else "./"
    debug(lambda: f"target: '{target}', root: '{root}'")

    if not exists(root):
        print(f"file '{root}' not found")
        sys.exit(1)

    dfs([root], target)
