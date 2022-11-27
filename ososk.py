import sys
import requests

base = "https://ososedki.com"
def_res = "604"  # default resolution
target_res = "1280"  # target resolution

if __name__ == "__main__":
    argv = sys.argv[1:]
    print(f"argv: {argv}")

    if len(argv) < 1:
        raise ValueError("please specify path to the input file")

    file = argv[0]
    failed = []

    print(f"opening file: {file}\n")

    with open(file) as f:
        all = f.read()
        all = all.replace("\t", "\n")
        lines = all.splitlines()

        # lines = f
        for line in lines:
            if not line:
                continue

            # line = line.replace("\n", "")

            # when copied from chrome, the links may start with 'Image'
            if line.startswith("Image"):
                line = line[5:]

            if not line.startswith("/images/a/"):
                continue

            r = line.rfind("/")
            filename = line[r+1:]

            url = (base + line).replace(f"/a/{def_res}/", f"/a/{target_res}/")
            # print(url)

            print(f"Downloading '{url}'")
            try:
                with open(filename, "wb") as df:
                    response = requests.get(url, timeout=20)
                    df.write(response.content)
                    print(f"Downloaded '{url}' as '{filename}'")
            except Exception as e:
                failed.append(line)
                print(f"Failed to download '{url}', error: {e}")
    
    if failed:
        failed_lines = "\n".join(failed)
        print(f"\nSome failed, please try again: \n{failed_lines}")
        with open(file, "w") as f:
            f.write(failed_lines)
