import time
import threading
from serial import Serial
import sys, getopt
import datetime
from decimal import Decimal

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

def callback(result, fileName):
    if result == None:
        print("Result is none")
        return
    print(result.Data, " is result.data")
    with open(fileName, "a") as file:
        data = result.Data.replace('\n', "").replace('\r', "")
        file.write("RCV: {0}\r\n".format(data))
        tmp_buffer= b""

# start_time = 0.0
# end_time = 0.0
device = ""
ser = None
baud = 115200
callbackFunc = callback
timeout_max = 5.0

def send(cmd):
    # Debug
    # print('sending command: ', cmd)
    # print(cmd.encode())
    ser.write(cmd.encode())

def parse(result, expect):
    
    data = ModemData()
    data.Data = result
    if (result.strip().find(expect.strip()) > -1):
        data.Success = True
    else:
        print("failed")
        data.Success = False
    
    return data

# Handles all commands through the script file
def handler(cmds, fileName):
    global ser, device, baud
    error_count = 0
    escape_loop = False
    # check to see if serial is already open if so close
    
    if ser == None:
        # Initializes serial port connection
        ser = Serial(device, baudrate=baud, parity='N', stopbits=1, bytesize=8, xonxoff=0, rtscts=0)
    
    for key in cmds["cfg"]:
        tmp_buffer = b""
        escape_loop = False
        # store the command and expected response for later use
        cmd = key[0]
        print("cmd: ", cmd)
        rsp = key[1]

        if rsp == "COMMENT" or rsp == "BLANK":
            result = parse(rsp, rsp)
            callbackFunc(result, fileName)
            continue
        
        # send command to modem
        send(cmd)
        # Reset start_time
        start_time = time.time()
        while(True):
            if (escape_loop == True):
                break
            
            # process timeout of command
            if ((time.time() - start_time) > timeout_max):
                print("timedout")
                break
            # process the modem's response
            while(ser.in_waiting > 0):
                # inefficient, but read one character at a time
                # TODO: refactor to read all bytes in serial buffer
                tmp_char = ser.read(1)
                if(tmp_char == b'\r'):
                    if not tmp_buffer or tmp_buffer.decode() == '\n':
                        tmp_buffer = b''
                        continue
                    # parse the accumulated buffer
                    if not (len(tmp_buffer) > 0):
                        continue
                    
                    print(rsp.strip(), " is rsp")
                    result = parse(tmp_buffer.decode(), rsp)
                    print ('received ', tmp_buffer)
                    # Check to see if we received what we were expecting
                    if(result.Success == True):
                        print("success")
                        if(callbackFunc != None):
                            callbackFunc(result, fileName)
                        # Escape time timeout loop
                        escape_loop = True
                    else:
                        error_count += 1
                            # print("error: cmd: ", cmd, " rsp: ", result.Data)

                    
                    # if cmd == "AT\r":
                    #     tmp_buffer = b''
                    #     continue
                    # else:
                    #     # Decodes the buffer, sets it to nothing,
                    #     # and writes to the file
                    #     tmp_buffer = tmp_buffer.decode().replace('\n', "")
                    #     tmp_buffer = tmp_buffer.replace('\r', "")
                    #     fileOpened.write("RCV: {0}\r\n".format(tmp_buffer))
                    #     tmp_buffer= b""
                else:
                    tmp_buffer += tmp_char
                
            # let outer while loop breathe
            time.sleep(.005)

def setup(comport, baudrate):
    global ser, device, baud
    device = comport
    baud = baudrate
    if ser == None:
        # Initializes serial port connection
        ser = Serial(comport, baudrate=baudrate, parity='N', stopbits=1, bytesize=8, xonxoff=0, rtscts=0)
    if ser.isOpen():
        ser.close()

    ser.open()
    time.sleep(5)