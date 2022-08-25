from genericpath import exists, isdir
from posixpath import abspath
import sys
import os

if __name__ == '__main__':
    root = "./" if len(sys.argv) < 2 else sys.argv[1]
    # print(f"root: {root}")

    # *.pom.xml specified
    if root.endswith("pom.xml"):
        if not exists(root):
            os.exit(1)

        print(root)
        sys.exit(0)

    # **/pom.xml
    if not root.endswith("/"):
        root = root + "/"

    cp = root + "pom.xml"
    if exists(cp):
        print(cp)
        sys.exit(0)

    # **/*/pom.xml
    l = os.listdir(root)
    for i in range(len(l)):
        if not isdir(l[i]):
            continue

        ll = os.listdir(l[i])
        for j in range(len(ll)):
            if ll[j].endswith("pom.xml"):
                print(root + l[i] + "/" + ll[j])
                sys.exit(0)

    sys.exit(1)
