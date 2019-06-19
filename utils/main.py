import sys, getopt, os, glob, datetime, json, time
from modem_handler import ModemHandler

path = ""
root = ""
key = ""
cert = ""

root_found = False
key_found = False
cert_found = False
log_found = False
arg_device_found = False
arg_baud_found = False
arg_config_found = False
device = ""
baudrate = -1
config = ""

def usageFunction():
    global p, r, k, c, l, co, b
    print("{0}\n{1}\n{2}\n{3}\n{4}\n\n".format(p, r, k, c, l))

usageDict = {
    "p": "-p, --path, is the path containing the certs",
    "r": "-r, --rootca, is the root certificate file name",
    "k": "-k, --key, is the key certificate file name",
    "c": "-c, --cert, is the client certificate file name",
    "l": "-l, --log, log output to console",
    "d": "-d, --device, the comport for the device to automate the task",
    "co": "-co, --config, the script file name and location of the scripting commands",
    "b": "-b, --baudrate, the baudrate of the serial device",
    "h": usageFunction,
}

p = usageDict['p']
r = usageDict['r']
k = usageDict['k']
c = usageDict['c']
l = usageDict['l']
d = usageDict['d']
co = usageDict['co']
b = usageDict['b']

def char_count(filename):
    key = ""
    key_len = 0

    # print("Opening %s", filename)

    with open(filename) as file:
        for line in file.readlines():
            key_len += len(line)
            key += line

    json_out = {
        "filename": filename.split("/")[-1],
        "key": key,
        "len": key_len,
    }
    if log_found:

        cmd = 'AT+QFUPL=\"%s\",%s,100' % (filename.split("/")[-1], str(key_len))

        print('file: %s\nlen: %s\ncmd: %s' % (filename.split("/")[-1], str(key_len), cmd))
        print(key)

def argParse(opts, args):
    found_path = False
    global path, root, key, cert, root_found, key_found, cert_found, log_found, device, baudrate, config, arg_device_found, arg_config_found, arg_baud_found
    for opt, arg in opts:
        optc = opt.lower()
        if optc in ['--help', '-h']:
            usageDict['h']()
            sys.exit()
        elif optc in ["--path", "-p"]:
            found_path = True
            if os.path.isdir(arg):
                path = arg
            else:
                print("Please enter a valid directory for the path.")
                sys.exit(1)
        elif optc in ["--rootca", "-r"]:
            root = arg
            root_found = True
        elif optc in ["--key", "-k"]:
            key = arg
            key_found = True
        elif optc in ["--cert", "-c"]:
            cert = arg
            cert_found = True
        elif optc in ["--device", "-d"]:
            arg_device_found = True
            device = arg
        elif optc in ["--baud", "-b"]:
            arg_baud_found = True
            if arg.isdigit():
                baudrate = int(arg)
            else:
                print("Baudrate must be an integer")
                sys.exit(1)
        elif optc in ["--config", "-co"]:
            arg_config_found = True
            config = arg
        
    if not found_path and not arg_config_found:
        print("Error: --path or --config is a required argument.")
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
        diction[str(count)] = item
        count += 1
    return diction

def setup():
    global baudrate, config, device
    try:
        if not config and baudrate <= 0 and not device:
            config = "quec.config.json"
            baudrate = 115200
            device = "/dev/tty.usbserial-FTB49XIB"
        with open(config) as json_file:
            cfg = json.load(json_file)
    except IOError as e:
        print("Oops: ", e)
        # sys.exit()

    return cfg

if __name__ == '__main__':
    print("Welcome to the Quectel BG96 certificate parser...\r\n")

    if not sys.argv[1:]:
        print("Error: please provide arugments.")
        sys.exit()
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:r:p:k:l:d:co:b:h', ['cert=', 'rootca=', 'path=', 'key=', 'log=', "device=", "config=", "baud=", 'help'])
    except getopt.GetoptError:
        print("Error: invalid argument.")
        sys.exit(2)
    
    if not opts and not args:
        print("Error, no parameters provided")
        usageDict['h']()
        sys.exit()
    
    argParse(opts, args)

    cfg = setup()

    # if arg_config_found:
    if baudrate == -1 and not device:
        print("Please enter {0} and {1} for the script to be able to automate the device.".format(co, b))
        sys.exit()
    else:
        if config and baudrate > 0 and device:
            mh = ModemHandler(device=device, config=config, baud=baudrate)
        else:
            mh = ModemHandler()
    
    print(arg_config_found)
            
    for key in cfg['cfg']:
        # pull command, expect and timeout from config
        cmd = key[0]
        data = ""
        byte = 0
        rsp = key[1]

        cmd_to = float(key[2])

        if cmd.find("file:") > -1:
            cert_filepath = cmd.replace("file:", "").strip()
            if os.path.isfile(cert_filepath):
                # Extract the file from the path
                mh.cert_filename = cert_filepath.split("/")[-1]
                mh.cert_filename = mh.cert_filename.split(".")[0]
                # print(cmd, " is cmd")
                with open(cert_filepath) as file:
                    for line in file.readlines():
                        data += line
                        byte += len(line)
                    
                    mh.cert_filedata = data
                    mh.cert_filesize = byte
                continue

        if cmd.find("AT+QFUPL") > -1:
            cmd = cmd.replace("{file}", mh.cert_filename).replace("{size}", str(mh.cert_filesize))
            cert_filepath = ""
            mh.cert_filename = ""
        
        rsp = mh.cmd_handler(cmd, rsp, cmd_to)