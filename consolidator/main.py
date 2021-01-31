import boto3
import json
import logging
from urllib.parse import unquote_plus

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

s3_client = boto3.client('s3')

priority_partners = ['Partner_B', 'Partner_A', 'Partner_D', 'Partner_D']


def consolidate_data(json_object):
    print("Consolidation of catalog data is started...")

    try:
        catalog_data = json.loads(json_object)
        print(catalog_data)
        print(type(catalog_data))
        for catalog in catalog_data:
            print(catalog['partner_name'])

    except Exception as ex:
        raise ex
    pass


def process_s3_events(s3_json_event):
    print("S3 event processing started...")

    bucket_name = None
    object_key = None
    try:
        for record in s3_json_event['Records']:
            bucket_name = record['s3']['bucket']['name']
            logger.debug("S3 bucket name: " + bucket_name)
            object_key = unquote_plus(record['s3']['object']['key'])
            
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            content = response['Body']
            json_object = content.read().decode('utf-8')
            print(json_object)

            consolidate_data(json_object)

    except Exception as ex:
        logger.error(ex)
        raise ex


def lambda_handler(event, context):
    print('Event: ' + str(event))
    print(json.dumps(event))

    try:
        for record in event['Records']:
            s3_event = record['body']
            print('Event body: ' + str(s3_event))
            s3_json_event = json.loads(s3_event)
            print(s3_json_event)
            print(type(s3_json_event))

            process_s3_events(s3_json_event)

    except Exception as ex:
        print(str(ex))
