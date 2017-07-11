"""

The purpose of this lambda function is to query Ravello and return a list and
count of all running VMs.

This is called asynchronously from the 'ravello' lambda function. This allows
the 'ravello' function to immediately return an HTTP 200 to Slack while this
function executes in the background.

"""
import boto3
import json
import logging
from urlparse import parse_qs
from base64 import b64decode
import pycurl
from io import BytesIO
import pprint
from urllib2 import Request, urlopen, URLError, HTTPError
#
logger = logging.getLogger()
logger.setLevel(logging.INFO)


ENCRYPTED_RAVELLO_USER = "AQICAHj49HEE8m06MDGiHk8OqJLX6IypkhfdVc1rfWY5AULrSgHZ0ERc2JNL1wKY/wYE9fKSAAAAcDBuBgkqhkiG9w0BBwagYTBfAgEAMFoGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMH52GAgIeBfjMPDKtAgEQgC3jawZ/yi9KRFlUXfyB+uwZleA/gq38j1oCqCWktrasXAgw9OB3SpNcvhyCVms="
DECRYPTED_RAVELLO_USER = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_RAVELLO_USER))['Plaintext']
ENCRYPTED_RAVELLO_PASSWORD = "AQICAHj49HEE8m06MDGiHk8OqJLX6IypkhfdVc1rfWY5AULrSgEhzJYYnEQfpE2j0J2LlMQpAAAAZzBlBgkqhkiG9w0BBwagWDBWAgEAMFEGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMH+wpnli1yhuhAbjvAgEQgCQLhk1sfEcnKzVRLju9+bdCMfg3OuY/Qxz1y/OZI3bwEytsfI0="
DECRYPTED_RAVELLO_PASSWORD = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_RAVELLO_PASSWORD))['Plaintext']

def respond():
    return {
        'statusCode': '200',
        'body': '',
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def post_to_slack(channel, response_type, response_url, msg):
    """Send messages to slack"""
    slack_message = {
        'Content-Type': 'application/json',
        'channel': channel,
        'response_type': response_type,
        'text': msg
    }
    req = Request(response_url, json.dumps(slack_message))
    # Record message in the CloudWatch log
    print('slack_message='+str(slack_message))
    try:
        response = urlopen(req)
        response.read()
        print("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        print("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        print("Server connection failed: %s", e.reason)


def handler(event, context):
    #print(type(event))
    #pprint.pprint(event)
    req_body = event['body']
    params = parse_qs(req_body)
    channel = params['channel_name'][0]
    response_url = params['response_url'][0]
    response_type = 'in_channel'

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
                post_to_slack(channel=channel,
                              response_type=response_type,
                              response_url=response_url,
                              msg=msg)
    msg = "Ravello total active VMs: %d"%total_active
    post_to_slack(channel=channel,
                  response_type=response_type,
                  response_url=response_url,
                  msg=msg)

    return respond()
