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



if __name__ == "__main__":
    print("Welcome to the future...")

    # char_count()

    if not sys.argv[1:]:
        print("Please provide file!")
        sys.exit()
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:r:p:k:h', ['cert=', 'rootca=', 'path=', "key=" ,'help'])
        # argParse(opts, args)

    except getopt.GetoptError:
        print("GetoptError")
        sys.exit(2)
    
    if not opts and not args:
        print("Error, no parameters provided")
        sys.exit()
    else:
        argParse(opts, args)

        root = os.path.join(path, root)
        key = os.path.join(path, key)
        cert = os.path.join(path, cert)

        if os.path.isfile(root):
            char_count(root)

        if os.path.isfile(key):
            char_count(key)

        if os.path.isfile(cert):
            char_count(cert)
        
