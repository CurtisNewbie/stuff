

import subprocess


if __name__ == '__main__':

    with subprocess.Popen(
            f"git branch", shell=True, stdout=subprocess.PIPE) as p:

        std = str(p.stdout.read(), 'utf-8')

        branches: set[str] = set()

        sp = std.splitlines()
        l = len(sp)
        for i in range(len(sp)):
            curr = sp[i]
            branches.add(curr.replace("*", "").strip())

        print(" ".join(branches))
