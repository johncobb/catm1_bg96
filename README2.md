## Creating a new Thing in Amazon's AWS IoT platform


### Login and create the Thing
 - Login to AWS
 - Under Services click IoT Core
 - Make sure US East 1 region is selected
 - Click Get started
 - Click Manage
 - Click Things (if not already selected)
 - Click Create
 - Click Create a single thing
 - Fill in the name and leave remaining fields blank... Click next
 - Click Create certificate
 - Download the keys (Will not use public key)
 - Download the CA for AWS IoT via the Download link
 - Pay close attention to the link endpoint will change based upon which Root CA is used
 - For example: -ats (amazon trusted certificates) will be remove from the endpoint when using VerisignLegacy Root CA 1
    - Download Amazon Root CA 1
    - Download Legacy Root CA 1

### Activate and create security policy
 - Activate your certificates by clicking the Activate button
 - Click attach a policy
 - Select the PIoT policy and click Register Thing
 - You should be taken back to the Manage Things dashboard


### Confirm your settings
Now we want to go into the device to make sure the certs are attached to the device an that the policies are attached to the certificates

 - Click the device
 - Click security
 - Click on the cert
 - Glance at the top to make sure the cert is ACTIVE
 - Click on policies and make sure you see the policy, in our case (PIoT)
 - Setup is complete

#### Gather the information you'll need to communicate with the Thing
Navigate back to the IoT Core dashboard and click Settings. Copy the endpoint for use with your device and place in a in a file for future use/setup.

 - Note the client id: in our case (datadog)
 - Note the endpoint: 
    - Root CA1/AWS Native: ```replace_with_your_name-ats.iot.us-east-1.amazonaws.com```
    - Legacy/Verisign: ```replace_with_your_name.iot.us-east-1.amazonaws.com```




TODO: Identify length of certs (use util/charcount.py)
CA Cert is Root CA (start out native one Root CA 1)
Client Cert is certificate.pem.crt
Private Cert is private.pem.key

```console
# get character count from cert files for use in AT commands
wc -c < path_to_file/file_name
```

### Automate the provisioning
```console
# navigate to util folder and activate environment
. env/bin/activate
python3 charcount.py -p ~/certs -r root.pem -k key.pem -c cert.pem
```
