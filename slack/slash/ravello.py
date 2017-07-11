"""

The purpose of this lambda function is threefold
  1. Verify a request comes from the correct location by verifying a token is
     correct.
  2. Asynchronously call the ravello_query lambda function
  3. Return an HTTP 200 before the slack timeout expires (3 seconds)

The intent is to spawn an async query and return a 200 as quickly as possible.

"""

import boto3
import json
import logging
from urlparse import parse_qs
from base64 import b64decode

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ENCRYPTED_EXPECTED_TOKEN = "AQICAHj49HEE8m06MDGiHk8OqJLX6IypkhfdVc1rfWY5AULrSgGGnwH2sHIv8KOAAuHzGcjdAAAAdjB0BgkqhkiG9w0BBwagZzBlAgEAMGAGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMWza3cGJjn7C3JPaKAgEQgDMAKZbfG1KF1UwQxWabePsnF8GDHF4vx94X//RZ0CW/1FCBdb2lKrmtnwA/RM1Tr2DRM3Y="
kms = boto3.client('kms')
expected_token = kms.decrypt(CiphertextBlob = b64decode(ENCRYPTED_EXPECTED_TOKEN))['Plaintext']


def respond():
    return {
        'statusCode': '200',
        'body': '',
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def handler(event, context):
    #print(type(event))
    #pprint.pprint(event)
    req_body = event['body']
    params = parse_qs(req_body)
    token = params['token'][0]

    if token != expected_token:
        logger.error("Request token (%s) does not match expected", token)
        raise Exception("Invalid request token")

    client = boto3.client('lambda')
    client.invoke_async(
        FunctionName='ravello_query',
        InvokeArgs=json.dumps(event)
    )

    return respond()
