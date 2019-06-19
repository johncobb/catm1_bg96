import datetime, time, json, sys, os
from serial import Serial

class ModemHandler(object):

    def __init__(self, device="/dev/tty.usbserial-FTB49XIB", config="quec.config.json", baud=115200):
        self.device = device
        self.config = config
        self.baud = 115200
        self.delimeters = ["OK", ">", "ERROR"]
        self.callbackFunc = self.modemDataReceived

        self.greeting()
        print(" - device: ", self.device)
        print(" - baud: ", self.baud)
        print(" - config: ", self.config)
        self.footer()
        self.cert_filedata = ""
        self.cert_filesize = 0
        self.cert_filename = ""
        
        self.ser = Serial(device, baudrate=baud, parity='N', stopbits=1, bytesize=8, xonxoff=0, rtscts=0)
        
    def greeting(self):
        print("\r\n")
        print("--------------------------------------")
        print(" BG96 Confiuration Utility")
    
    def footer(self):
        print("--------------------------------------")
    
    def modemDataReceived(self, buffer):
        print('Callback function modemDataReceived ', buffer)

    def line_handler(self, buffer, rsp):
        return buffer.find(rsp) > -1

    def expect(self, result, parm):
        data = ModemData()

        if result.find(parm) > -1:
            data.ExpectFound = True
            data.ExpectData = result
        
        return data
    
    def send(self, cmd):
        print("sending command: ", cmd)
        self.ser.write(cmd.encode())
    
    def prov_tick(self, cmd_ts, rsp, cmd_to):
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
            while(self.ser.in_waiting > 0):
                # read next line form serial port
                line = self.ser.readline().decode("utf-8")
                # accumulate a local buffer
                buffer += line

                # did we get a delimeter?
                # delimeter_found = line_handler(buffer)
                delimeter_found = self.line_handler(buffer, rsp)
                # rps_found = rsp_handler(buffer, rsp)

            if delimeter_found:
                # data = expect(buffer, rsp)
                # if data.ExpectFound:
                #     print("ExpectData: ", data.ExpectData)
                self.callbackFunc(buffer)
                print("elapsed: ", elapsed)
                self.footer()
                break

            # let outer while loop breathe
        time.sleep(.1)
    
    def cmd_handler(self, cmd, rsp, cmd_to):
        data = ""
        byte = 0
        
        # store the start time of the command
        cmd_ts = time.time()

        # send command to modem
        self.send(cmd)

        self.prov_tick(cmd_ts, rsp, cmd_to)

        if self.cert_filedata and self.cert_filesize > 0:
            cmd_ts = time.time()

            self.send(self.cert_filedata)
            self.prov_tick(cmd_ts, "QFUPL:", cmd_to)

            self.cert_filedata = ""
            self.cert_filesize = 0
        return "OK"

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