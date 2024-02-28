import re
import sys
import re
import subprocess
from os import walk
from os.path import join

def cli_run(cmd: str):
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) as p:
        if p.returncode != None and p.returncode != 0:
            raise ValueError(f"'{cmd}' failed, returncode {p.returncode}")
        std = str(p.stdout.read(), 'utf-8')
        return std

def current_branch():
    out = cli_run("git status")
    lines = out.splitlines()
    for l in lines:
        m = re.match('On branch ([^\s]+)', l)
        if m:
            return m[1]

def all_tags():
    return cli_run("git tag")

def current_tag():
    out = cli_run("git describe --tags --abbrev=0")
    return out.strip()

def parse_beta(tag):
    pat = re.compile('(v.+).beta.*')
    m = pat.match(tag)
    if m:
        return m[1]
    return tag

def guess_next(last):
    if is_beta(last): return incr_beta(last)
    return incr_release(last)

def incr_release(v):
    pat = re.compile('(v?\d+\.\d+\.)(\d+)\.?.*')
    m = pat.match(v)
    return m[1] + str(int(m[2]) + 1)

def incr_beta(v):
    pat = re.compile('^v?\d+\.\d+\.\d+$')
    m = pat.match(v)
    if m: return v + "-beta.1"

    pat = re.compile('(v?\d+\.\d+\.\d+-beta\.)(\d+)')
    m = pat.match(v)
    return m[1] + str(int(m[2]) + 1)

def is_beta(v):
    pat = re.compile('(v?\d+\.\d+\.\d+-beta\.)(\d+)')
    return pat.match(v)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        last = current_tag()
        if not last or last == 'main' or last == 'master':
            exit(0)
        guessed = guess_next(last)
        print()
        print(f"Last release is {last}. Are you planning to release {guessed} ?")
        print()
        print(f"release {guessed}")
        print()
        exit(1)

    branch = current_branch()
    target = sys.argv[1]

    latest_tag = current_tag().strip()
    if latest_tag == target:
        print(f"{latest_tag} has been released")
        exit(1)

    target_release = parse_beta(target)
    if target_release != target and target_release in all_tags().splitlines():
        print(f"{target_release} has been released")
        exit(1)

    version_file = None
    for (dir_path, dir_name, file_names) in walk("."):
        for fn in file_names:
            if fn == 'version.go':
                version_file = join(dir_path, fn)

    # print(version_file)

    if version_file:
        pkg = "main"

        with open(version_file, "r") as f:
            lines = f.readlines()
            for l in lines:
                pat = re.compile('package (.*)')
                m = pat.match(l)
                if m: pkg = m[1]

        with open(version_file, "w") as f:
            f.writelines([
                f"package {pkg}\n",
                "\n",
                "const (\n",
                f"\tVersion = \"{target}\"\n"
                ")\n"
                ""
            ])

    print(cli_run("go fmt ./..."))
    print(cli_run(f"git commit -am \"Release {target}\""))
    print(cli_run(f"git tag \"{target}\""))
    print("Done, it's time to push your tag to remote origin! :D")
    print(f"\ngit push && git push origin {target}\n\n")
