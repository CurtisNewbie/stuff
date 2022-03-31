import sys

def split(text, delimiter):
    print(text.split(delimiter))

def print_help():
    print('arg[0] - text to be splited')
    print('arg[1] - delimiter')

if __name__ == "__main__"   :
    if len(sys.argv) != 3: 
        print_help()
        raise Exception('Illegal Arguments')  

    text = sys.argv[1]
    delimiter = sys.argv[2]
    split(text, delimiter)


