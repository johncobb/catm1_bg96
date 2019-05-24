import sys, getopt, os
import json

path = ""
root = ""
key = ""
cert = ""

def char_count(filename):

    key = ""
    key_len = 0
    # filename = input("Please enter the file name: ")

    print("Opening %s", filename)

    with open(filename) as file:
        for line in file.readlines():
            key_len += len(line)
            key += line

    json_out = {
        "filename": filename.split("/")[-1],
        "key": key,
        "len": key_len
    }

    print(json.dumps(json_out, indent=4, sort_keys=True))

def argParse(opts, args):
    global path, root, key, cert
    for opt, arg in opts:
        optc = opt.lower()
        if optc in ['--help', '-h']:
            pass
        elif optc in ["--path", "-p"]:
            if os.path.isdir(arg):
                path = arg
                print(arg)
            else:
                print("Please enter a valid directory for the path.")
                sys.exit(1)
        elif optc in ["--rootca", "-r"]:
            root = arg
        elif optc in ["--key", "-k"]:
            key = arg
        elif optc in ["--cert", "-c"]:
            cert = arg

    print(path, " is path")
    if os.path.isfile(path + root):
        print("hehe")

if __name__ == "__main__":
    print("Welcome to the future...")

    # char_count()

    if not sys.argv[1:]:
        print("Please provide file!")
        sys.exit()
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:r:p:k:h', 
        ['cert=', 'rootca=', 'path=', "key=" ,'help'])
    except getopt.GetoptError:
        print("GetoptError")
        sys.exit(2)
    
    argParse(opts, args)

    char_count(path + "/" + root)
    char_count(path + "/" + key)
    char_count(path + "/" + cert)