
![Quectel BG96](https://www.quectel.com/UploadImage/Product/20171016161456212.png)


## Configuring the Quectel BG96 for connectivity with Amazon's AWSIoT platform
Some or all references to Quectel's PDFs require registration on the Quectel website:

### Prerequisites:
 - UMTS&LTEEVB - KIT
 - Download the latest version of PDF(s) listed in the References section below

### Connecting the UMTS&LTEEVB - KIT

By default, the modem is powered down. Momemtarily press the PWRKEY (500 ms) on the evaluation kit to initiate the powerup sequence. The red POWER led and green STATUS led should be illuminated. You may also see the blue NET_STA led flashing a sequence of status messages. Consult the PDF to decipher. Now, let's get started communicating with the modem.

Connect the evaluation to a USB power source. Next connect the (provided) USB to Serial cable to your computer. Issue the commands below to determine which port to connect to to issue AT commands.

```console
ls /dev | grep tty.us
tty.usbserial-FTASWORM
tty.usbserial-FTWKWE7H
```

On my computer the `tty.usbserial-FTWKWE7H` interface was the one I was looking for. Now fire up your favorite terminal software to begin communicating with the modem. In my example I will be using cu. After a successful connection is established issue an AT followed by a carriage return and the modem should respond with OK.

```console
sudo cu -l tty.usbserial-FTASWORM -s 115200
Connected.
AT
OK
```

As a personal preference I like to see what I'm typing into the terminal so the first command I issue is an `ATE1` which turns the echo on. Anything typed into the terminal will be echoed back to you . When designing an application to automate the modem you'll want to turn this command off by issuing `ATE0`. 

The commands in the snippet below are the initialization commands to prepare the modem for communication on the network. There can be many issues during this process so follow the Keep It Simple Stupid method. Make sure you have a SIM inserted. Make sure the SIM is active. Make sure you have the correct APN number to verify.

#### General initialization and network preparation
```console
# set verbose logging
AT+CMEE=2
OK

# pin status
AT+CPIN?
+CPIN: READY

# sim status
AT+QSIMSTAT?
+QSIMSTAT: 0,1

# query operator selection
AT+COPS?
+COPS: 0,0,"T-Mobile Hologram",0

# query network registration
AT+CGREG?
+CGREG: 0,5


# power down device
AT+QPOWD

```

### I cannot get my modem to register
Well join the club. When I first set out to configure this and other modems that are Cat-M1 and NB-IoT they would not connect to the network. You have to set the network fallback technologies via the network scan parameter. This will allow the network to fallback to GSM in the event Cat-M1 or NB-IoT are not activated in your area. The command that worked for me is listed below.

```console
# 01 NB-IoT
# 02 Cat-M1
# 03 GSM

# first try Cat-M1 then try GSM and NB-IoT is just finally
AT+QCFG="nwscan",020301
```



### Establish a TCP connection:
```console

# set APN
AT+QICSGP=1,1,"hologram", "", "", 1
OK

# activate context
AT+QIACT=1
OK

# query context
AT+QIACT?
OK


# open connection
AT+QIOPEN=1,1,"TCP","220.180.239.201",8713,0,0
OK

+QUOPEN: 1,566

# disconnect
AT+QIDEACT=1
OK
```



### References:

 - Quectel_BG96_AT_Commands_Manual_V2.3 (PDF)
 - Quectel_BG96_TCP(IP)_AT_Commands_Manual_V1.0 (PDF)
 - Quectel_BG96_SSL_AT_Commands_Manual_V1.0 (PDF)
 - Quectel_BG96_GNSS_AT_Commands_Manual_V1.1 (PDF)
 - Quectel_BG96_MQTT_Application_Note_V1.0 (PDF)