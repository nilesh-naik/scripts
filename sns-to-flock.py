import boto3
import logging
import os
import requests

from base64 import b64decode

# The base-64 encoded, encrypted key (CiphertextBlob)
# stored in the kmsEncryptedHookUrl environment variable
ENCRYPTED_HOOK_URL = os.environ['kmsEncryptedHookUrl']
# The Flock channel to send a message to stored
# in the flockChannel environment variable
FLOCK_CHANNEL = os.environ['flockChannel']

HOOK_URL = 'https://' + boto3.client('kms').decrypt(
        CiphertextBlob=b64decode(ENCRYPTED_HOOK_URL)
    )['Plaintext'].decode('utf-8')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('Event: ' + str(event))
    subject = event['Records'][0]['Sns']['Subject']
    message = event['Records'][0]['Sns']['Message']
    logger.info('Subject: ' + subject)
    logger.info('Message: ' + message)

    flock_message = {
        'channel': FLOCK_CHANNEL,
        'message': message
    }

    try:
        req = requests.post(HOOK_URL, data=flock_message)
        logger.info("Message posted to %s", flock_message['channel'])
    except Exception as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
