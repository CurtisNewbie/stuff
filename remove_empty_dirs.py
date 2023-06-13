import os

pdir ='./'
subdirs = [ f.path for f in os.scandir(pdir) if f.is_dir() ]
for d in subdirs:
    if len(os.listdir(d)) < 1:
        print(f"{d} is empty, removing it")
        os.rmdir(d)