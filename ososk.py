import sys

base = "https://ososedki.com"
def_res = "604" # default resolution
target_res = "1280" # target resolution

if __name__ == "__main__":
    argv = sys.argv[1:]
    print(f"argv: {argv}")

    if len(argv) < 1:
        raise ValueError("please specify path to the input file")

    file = argv[0]

    print(f"opening file: {file}\n")

    with open(file) as f:
        for line in f:

            # when copied from chrome, the links may start with 'Image'
            if line.startswith("Image"):
                line = line[5:]

            if not line.startswith("/images/a/"):
                continue
        
            r = line.rfind("/")
            filename = line[r+1:]

            curl = f"curl \"{base + line}\" -o \"{filename}\""
            curl =  curl.replace(f"/a/{def_res}/", f"/a/{target_res}/")
            curl = curl.replace("\n", "")
            print(curl)
