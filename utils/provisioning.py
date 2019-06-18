import time
import threading
from serial import Serial
import sys, getopt
import datetime
import json
import os

### arg parsing from command line ###
arg_device_found = False
arg_baud_found = False
arg_config_found = False

class ModemResponse:
    OK = "OK"
    ERROR = "ERROR"
    CONNECT = "CONNECT"
    NOCARRIER = "NO CARRIER"
    PROMPT = ">"
    CMGS = "+CMGS:"
    CREG = "+CREG:"

class ModemData:
    Success = False
    Data = ModemResponse.OK
    ExpectFound = False
    ExpectData = ""

# serial vars
ser = None
device = ""
baud = 115200
callbackFunc = None

error_count = 0

# command timeout vars
app_timeout = 0.0
timestamp = 0.0


delimeters = ["OK", ">", "ERROR"]
buffer = ""

def greeting():
    print("\r\n")
    print("--------------------------------------")
    print(" BG96 Confiuration Utility")

def footer():
    print("--------------------------------------")

def prov_tick(cmd_ts, rsp, cmd_to):
    buffer = ""
    # reset delimeter_found flag
    delimeter_found = False
    rsp_found = False
    while(True):
        # calculate elapsed time
        elapsed = (time.time() - cmd_ts)
        # if the command times out break out of the loop
        if (elapsed > cmd_to):
            print("Error: Modem timeout waiting response.")
            break

        result = ModemData()

        # process the modem's response
        while(ser.in_waiting > 0):
            # read next line form serial port
            line = ser.readline().decode("utf-8")
            # accumulate a local buffer
            buffer += line

            # did we get a delimeter?
            # delimeter_found = line_handler(buffer)
            delimeter_found = line_handler(buffer, rsp)
            # rps_found = rsp_handler(buffer, rsp)

        if delimeter_found:
            # data = expect(buffer, rsp)
            # if data.ExpectFound:
            #     print("ExpectData: ", data.ExpectData)
            callbackFunc(buffer)
            print("elapsed: ", elapsed)
            footer()
            break

        # let outer while loop breathe
        time.sleep(.1)

def cfg_handler(cfg):
    cmd2 = ""
    rsp2 = ""
    cmd_to2 = 0
    cert_filepath = ""
    cert_filename = ""
    cert_filedata = ""
    cert_filesize = 0
    # check to see if serial is already open if so close
    if (ser.isOpen()):
        ser.close()

    # open serial
    ser.open()
    next_is_pub = False
    # loop through each command
    for key in cfg["cfg"]:
        
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
                cert_filename = cert_filepath.split("/")[-1]
                print(cmd, " is cmd")
                with open(cert_filepath) as file:
                    for line in file.readlines():
                        data += line
                        byte += len(line)
                    
                    cert_filedata = data
                    cert_filesize = byte
                continue

        if cmd.find("AT+QFUPL") > -1:
            cmd = cmd.replace("{file}", cert_filename).replace("{size}", str(cert_filesize))
            cert_filepath = ""
            cert_filename = ""
        
        
        # store the start time of the command
        cmd_ts = time.time()

        # send command to modem
        send(cmd)

        prov_tick(cmd_ts, rsp, cmd_to)

        if cert_filedata and cert_filesize > 0:
            cmd_ts = time.time()

            send(cert_filedata)
            prov_tick(cmd_ts, "QFUPL:", cmd_to)

            cert_filedata = ""
            cert_filesize = 0

    # close the port
    if (ser.isOpen()):
        ser.close()

def line_handler(buffer, rsp):
    
    return (buffer.find(rsp) > -1)

def expect(result, parm):
    data = ModemData()

    if (result.find(parm) > -1):
        data.ExpectFound = True
        data.ExpectData = result

    return data

"""
Write command to device
"""
def send(cmd):
    print('sending command: ', cmd)
    ser.write(cmd.encode())

def modemDataReceived(buffer):
    print('Callback function modemDataReceived ', buffer)

def setup(device="/dev/tty.usbserial-FTB49XIB", config="quec.config.json", baud=115200):
    global ser, callbackFunc
    greeting()
    print(" - device: ", device)
    print(" - baud: ", baud)
    print(" - config: ", config)
    footer()

    try:
        print(config, " config")
        with open(config) as json_file:
            cfg = json.load(json_file)

            ser = Serial(device, baudrate=baud, parity='N', stopbits=1, bytesize=8, xonxoff=0, rtscts=0)
            callbackFunc = modemDataReceived

            cfg_handler(cfg)
    except IOError as e:
        print("Oops: ", e)
