import subprocess

flag_translate_dict: dict[str, str] = {
    "A": "Added",
    "M": "Modified",
    "D": "Deleted",
    "R": "Renamed"
}


def translate_flag(flag: str) -> str:
    t = flag_translate_dict.get(flag.upper(), None)
    if t == None:
        raise ValueError(f"Unable to translate flag: {flag}")
    return t


if __name__ == '__main__':
    with subprocess.Popen(
            f"git diff --staged --raw", shell=True, stdout=subprocess.PIPE) as p:

        diff = str(p.stdout.read(), 'utf-8')

        '''
        :000000 100644 0000000 a5d3b63 A        gencmt.py
        :100644 000000 fe43d05 0000000 D        hosts
        :100644 100644 1f5ec8c 1822b21 M        lbranch.py
        :100755 100755 10b0158 10b0158 R100     split.py        splits.py
        :100644 100644 0b9c619 7e81f5f M        tools.sh
        '''

        sp = diff.splitlines()
        for i in range(len(sp)):
            line = sp[i]
            flag = line[31:32]
            # print(flag)

            # renamed a file
            # print(f"flag: {flag}")
            if flag.upper() == "R":
                file = line[32:]
                # print(f"f0: {file}")
                for j in range(len(file)):
                    if file[j] == "\t":
                        file = file[j:].strip()
                        break

                #print(f"f1: {file}")

                k = file.find("\t")
                if k > -1:
                    file = file[:k]
            else:
                file = line[32:].strip()
            # print(f"f2: {file}")

            translated = translate_flag(flag) + ":"
            print(f"{translated:<10} {file}")
