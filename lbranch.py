from genericpath import exists
import subprocess
import os

BRANCH_PREFIX = "On branch "
BRANCH_PREFIX_LEN = len(BRANCH_PREFIX)

if __name__ == '__main__':
    root = "./"
    entries: list[str] = os.listdir(root)

    for i in range(len(entries)):
        # print(entries[i])
        folder = entries[i]
        # print(f"folder: {folder}")
        if not os.path.isdir(folder):
            continue

        if not exists(folder + "/.git"):
            continue

        with subprocess.Popen(
                f"git -C {folder} status", shell=True, stdout=subprocess.PIPE) as p:

            std = str(p.stdout.read(), 'utf-8')
            # print(std)

            l = len(std.splitlines())
            if l == 0:
                continue

            firstline = std.splitlines()[0]
            # print("firstline: ", firstline)

            i = firstline.find(BRANCH_PREFIX)
            if i < 0:
                continue

            branch = firstline[i + BRANCH_PREFIX_LEN:]
            print(f"{folder:<30} {branch}")
