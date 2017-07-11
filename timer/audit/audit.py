"""

Description:
 A simple lambda function which will run a quick audit Ravello VMs.

"""
from __future__ import print_function
import json
import logging
import boto3
import pycurl
from io import BytesIO
import json

from base64 import b64decode
from urllib2 import Request, urlopen, URLError, HTTPError

SLACK_CHANNEL = '#training'  # Enter the Slack channel to send a message to
#SLACK_CHANNEL = '#play'  # debug


# noinspection PyPep8
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#
# The encrypted values below were created using the following process
#
# 1. Create a new encryption key in AWS by going to the main console
#    and selecting IAM->Encryption Keys->Create key
#
# 2. Go to your local command line and encrypt your strings using the
#    newly-created key (e.g. 'foo') like this:
#       aws kms encrypt --key-id alias/foo --plaintext "secrets and lies"
#
# 3. The resulting output are the ENCRYPTED_<whatever> values pasted below
#
# They can only be deciphered by the 'foo' key. That key is associated with
# this lambda function using the "KMS key" option in the lambda Advanced
# settings section of the Configuration tab.
#
ENCRYPTED_SLACK_HOOK_URL = "AQICAHj49HEE8m06MDGiHk8OqJLX6IypkhfdVc1rfWY5AULrSgEYAMIwOQh7L+oWOOhm4UsQAAAApzCBpAYJKoZIhvcNAQcGoIGWMIGTAgEAMIGNBgkqhkiG9w0BBwEwHgYJYIZIAWUDBAEuMBEEDPqLY0VrGynYTBnl5QIBEIBgNgMJgzx5yptjBk5dBBjC9DSJSAsLDd/uDle6r/dHa453czKeFhr8bX5ML5S4NF+UN6ysmqzYeQdK0HHTdIheszvWLw76c3gpfzu9UXKaXk3B8/FspfQM72siyzZHWp19"
DECRYPTED_SLACK_HOOK_URL = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_SLACK_HOOK_URL))['Plaintext']
SLACK_HOOK_URL = "https://%s" % DECRYPTED_SLACK_HOOK_URL
ENCRYPTED_RAVELLO_USER = "AQICAHj49HEE8m06MDGiHk8OqJLX6IypkhfdVc1rfWY5AULrSgHZ0ERc2JNL1wKY/wYE9fKSAAAAcDBuBgkqhkiG9w0BBwagYTBfAgEAMFoGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMH52GAgIeBfjMPDKtAgEQgC3jawZ/yi9KRFlUXfyB+uwZleA/gq38j1oCqCWktrasXAgw9OB3SpNcvhyCVms="
DECRYPTED_RAVELLO_USER = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_RAVELLO_USER))['Plaintext']
ENCRYPTED_RAVELLO_PASSWORD = "AQICAHj49HEE8m06MDGiHk8OqJLX6IypkhfdVc1rfWY5AULrSgEhzJYYnEQfpE2j0J2LlMQpAAAAZzBlBgkqhkiG9w0BBwagWDBWAgEAMFEGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMH+wpnli1yhuhAbjvAgEQgCQLhk1sfEcnKzVRLju9+bdCMfg3OuY/Qxz1y/OZI3bwEytsfI0="
DECRYPTED_RAVELLO_PASSWORD = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_RAVELLO_PASSWORD))['Plaintext']


def post_to_slack(msg):
    # uncomment to debug
    #    print(msg)
    #    return
    slack_message = {
        'channel': SLACK_CHANNEL,
        'text': msg
    }
    req = Request(SLACK_HOOK_URL, json.dumps(slack_message))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)


# noinspection PyUnusedLocal
def handler(event, context):

    total_active = 0
    buf = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://cloud.ravellosystems.com/api/v1/applications')
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.setopt(c.HTTPHEADER, ['Accept: application/json'])
    c.setopt(c.USERPWD, "%s:%s" % (DECRYPTED_RAVELLO_USER,DECRYPTED_RAVELLO_PASSWORD))
    c.perform()
    j = json.loads(buf.getvalue())
    for item in j:
        if "deployment" in item:
            active = item["deployment"]["totalActiveVms"]
            total_active += active
            if active:
                msg = "Lab: %s, Owner: %s, VMs: %d" % (item["name"], item["owner"], active)
                post_to_slack(msg)
    if total_active:
        post_to_slack("Ravello total active VMs: %d"%total_active)

# Uncomment to debug
# handler("", "")
