
![Quectel BG96](https://www.quectel.com/UploadImage/Product/20171016161456212.png)


## Configuring the Quectel BG96 for connectivity with Amazon's AWSIoT platform
Some or all references to Quectel's PDFs require registration on the Quectel website:

### Prerequisites:
 - UMTS&LTEEVB - KIT
 - Download the latest version of PDF(s) listed in the References section below

### Connecting the UMTS&LTEEVB - KIT

By default, the modem is powered down. Momemtarily press the PWRKEY (300 ms) on the evaluation kit to initiate the powerup sequence. The red POWER led and green STATUS led should be illuminated. You may also see the blue NET_STA led flashing a sequence of status messages. Consult the PDF to decipher. Now, let's get started communicating with the modem.

Connect the evaluation to a USB power source. Next connect the (provided) USB to Serial cable to your computer. Determine which serial device to connect to by issuing the command below:

```console
ls /dev | grep tty.us
tty.usbserial-FTASWORM
tty.usbserial-FTWKWE7H
```

On my computer the `tty.usbserial-FTWKWE7H` interface was the one I was looking for. Now fire up your favorite terminal software to begin communicating with the modem. In my example I will be using `cu`. After a successful connection is established issue an AT followed by a carriage return and the modem should respond with OK.

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

# signal quality (response: <rssi>, <ber>)
AT+CSQ
+CSQ: 13,99

OK

# apply PSM, enable network registration and location information
AT+CGREG=4
OK

# query registration status
AT+CGREG?
+CGREG: 4,5,"66C0","1042","0",,,,"00000000","01100000","00000000"

OK

# query network info
AT+QNWINFO
+QNWINFO: "EDGE","310260","GSM 1900",613

OK

# query name of registered network
AT+QSPN
+QSPN: "T-Mobile","T-Mobile","Hologram",0,"310260"

OK



# power down device
AT+QPOWD

```

### I cannot get my modem to register
Well join the club. When I first set out to configure this and other modems that are Cat-M1 and NB-IoT they would not connect to the network. You have to set the network fallback technologies via the network scan parameter. This allows the network to fallback to GSM in the event Cat-M1 or NB-IoT are not active in your area. The command that worked for me is listed below.

```console
# 01 NB-IoT
# 02 Cat-M1
# 03 GSM

# first try Cat-M1 then try GSM and NB-IoT is just finally
AT+QCFG="nwscanseq",020301
OK
```

### Configuring and connecting to Amazon's AWSIoT via SSL

The following commands configure a SSL based connection the Amazon IoT platform. Refer to the Quectel_BG96_MQTT_Application_Note_V1.0 pdf to get a more in depth view of each command.

```console

# configure MQTT session to use SSL mode
AT+QMTCFG=”SSL”,0,1,2
OK

# if SSL authentication mode is "server authentication" store CA certificate to RAM
AT+QFUPL="root.pem",1758,100
CONNECT
<Input the root.pem data, the size is 1758 bytes> +QFUPL: 1758,384a
OK

# if SSL authentication mode is "server authentication" store CC certificate to RAM
AT+QFUPL="cert.pem",1220,100
CONNECT
<Input the cert.pem data, the size is 1220 bytes> +QFUPL: 1220,2d53
OK

# if SSL authentication mode is "server authentication" store CK certificate to RAM
AT+QFUPL="key.pem",1679,100
CONNECT
<Input the private.pem.key data, the size is 1679 bytes> +QFUPL: 1679,335f
OK

# configure CA certificate
AT+QSSLCFG="cacert",2,"root.pem"
OK

# configure CC certificate
AT+QSSLCFG="clientcert",2,"cert.pem"

# configure CK certificate
AT+QSSLCFG="clientkey",2,"key.pem"
OK

# SSL authentication mode: server authentication
# TODO: The following command errored first several times we issued
AT+QSSLCFG="seclevel”,2,2
OK

# SSL authentication version
AT+QSSLCFG="sslversion”,2,4
OK

# cipher suite
TODO: documentation shows quotes around 0xffff
AT+QSSLCFG="ciphersuite”,2,0xffff
OK

# ignore time of authentication
AT+QSSLCFG="ignorelocaltime",1
OK

```

### Let's connect already!

Now is a good time for a coffee break. I like to take time and enjoy the moment of truth or at least have enough caffeine in my system to continue down the path of debugging connectivity issues.

```console
# start MQTT SSL connection
AT+QMTOPEN=0, "{account.name}-ats.iot.us-east-1.amazonaws.com",8883
OK
+QMTOPEN: 0,0

# connect to MQTT server
AT+QMTCONN=0,"datadog"
OK
+QMTCONN: 0,0,0

# subscribe to topics
AT+QMTSUB=0,1,"$aws/things/datadog/shadow/update/accepted",1
OK
+QMTSUB: 0,1,0,1

# publish messages
AT+QMTPUB=0,1,1,0,"$aws/things/datadog/shadow/update/accepted"
>This is publish data from client OK
+QMTPUB: 0,1,0

# data received from subscribed topic
+QMTRECV: 0,1,"$aws/things/datadog/shadow/update/accepted",This is publish data from client"

# disconnect a client from MQTT server
AT+QMTDISC=0
OK +QMTDISC: 0,0
```



### Establish a TCP connection:
The following does fall outside the scope of this tutorial however I felt it is relevant to include. Establishing a TCP connection is a good way to exercise the modem to ensure we have connectivity. 

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