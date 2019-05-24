import sys, getopt, os, glob
import json

path = ""
root = ""
key = ""
cert = ""
rootb = False
keyb = False
certb = False
genb = False
usageDict = {
    "p": "-p, --path, is the path containing the files",
    "r": "-r, --rootca, is the root certificate file name",
    "k": "-k, --key, is the key certificate file name",
    "c": "-c, --cert, is the client certificate",
    'g': '-g, --gen, does',
    "h": usageFunction()
}

p = usageDict['p']
r = usageDict['r']
k = usageDict['k']
c = usageDict['c']
g = usageDict['g']

def usageFunction():
    global p, r, k, c, g
    print("{0}\n{1}\n{2}\n{3}\n{4}".format(p, r, k, c, g))

def char_count(filename):
    key = ""
    key_len = 0

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
    found_path = False
    global path, root, key, cert, rootb, keyb, certb, genb
    for opt, arg in opts:
        optc = opt.lower()
        if optc in ['--help', '-h']:
            usageDict['h']
        elif optc in ["--path", "-p"]:
            found_path = True
            if os.path.isdir(arg):
                path = arg
            else:
                print("Please enter a valid directory for the path.")
                sys.exit(1)
        elif optc in ["--rootca", "-r"]:
            root = arg
            rootb = True
        elif optc in ["--key", "-k"]:
            key = arg
            keyb = True
        elif optc in ["--cert", "-c"]:
            cert = arg
            certb = True
        elif optc in ['--gen', '-g']:
            pass
        
    if not found_path:
        print("Error: --path is a required argument.")
        sys.exit()

def getFilesInDir(path):
    toReturn = []
    for item in glob.glob(path + "/*"):
        toReturn.append(item)
    return toReturn

def listToDictionary(list):
    count = 1
    diction = {}
    for item in list:
        if isinstance(item, str):
            toPrint = str(count) + " - " + item
        else:
            toPrint = str(item[0]) + " - " + item[1].split("/")[-1]
            item = item[1]

        print(str(toPrint))
        dicttoconvert[str(count)] = item
        count += 1
    return diction

if __name__ == "__main__":
    print("Welcome to the future...")

    if not sys.argv[1:]:
        print("Error: please provide arugments.")
        sys.exit()
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:r:p:k:h', ['cert=', 'rootca=', 'path=', "key=" ,'help'])
    except getopt.GetoptError:
        print("Error: invalid argument.")
        sys.exit(2)
    
    if not opts and not args:
        print("Error, no parameters provided")
        usageDict['h']
        sys.exit()
    
    argParse(opts, args)

    root = os.path.join(path, root)
    key = os.path.join(path, key)
    cert = os.path.join(path, cert)

    if path and not root and not key and not cert and not genb:
        print("Please enter either {0}, {1}, {2}, or {3}.".format(r, k, c, g))
        sys.exit(2)

    if os.path.isfile(root):
        char_count(root)

    if os.path.isfile(key):
        char_count(key)

    if os.path.isfile(cert):
        char_count(cert)
        
