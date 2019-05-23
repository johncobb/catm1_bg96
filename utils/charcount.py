import sys, getopt
import json

def char_count():

    key = ""
    key_len = 0
    filename = input("Please enter the file name: ")

    print("Opening %s", filename)

    with open(filename) as file:
        for line in file.readlines():
            key_len += len(line)
            key += line

    json_out = {
        "key": key,
        "len": key_len
    }

    print(json.dumps(json_out, indent=4, sort_keys=True))

if __name__ == "__main__":

    print("Welcome to the future...")
    char_count()

    # if not sys.argv[1:]:
    #     print("Please provide file!")
    #     sys.exit()

    # args = sys.argv
    # try:
    #     opts, args = getopt.getopt(args[1:], 'c:r:p:h', 
    #     ['cert=', 'rootca=', 'private=', 'help'])
    # except getopt.GetoptError:
    #     print("GetoptError")
    #     sys.exit(2)

    
    
