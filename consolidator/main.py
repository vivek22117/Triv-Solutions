import boto3
import json
import logging
import datetime
import sys
import os
from urllib.parse import unquote_plus
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Use IAM lambda role to generate credentials instead of hard coded ACCESS_KEY & SECRET_KEY
s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')
sns_client = boto3.client("sns")

# Can be passed via Lambda environment variables
# TABLE_NAME = os.environ['dynamo_db_table']
TABLE_NAME = 'Partners-Priority-Storage'
DESTINATION_BUCKET = 'partners-consolidated-data'
TOPIC_ARN = 'arn:aws:sns:us-east-1:XXXXXXXX:partners-data-notification'

partners_list = []


# Create dictionary class to store key value pair and append it.
class PartnerDict(dict):

    def __init__(self):
        super().__init__()
        self.data_dict = dict()

    def add(self, key, value):
        self[key] = value


def lambda_handler(event, context):
    global partners_list
    logger.info('Event: ' + str(event))

    # Fetch partners priority list for filtering catalog data
    fetch_partners_list()
    logger.info("Partner's Priority List: " + str(partners_list))
    result = []
    s3_json_event = None
    try:
        for record in event['Records']:
            s3_event = record['body']
            logger.info('Event body: ' + str(s3_event))
            s3_json_event = json.loads(s3_event)
            logger.info(s3_json_event)

            # Processing of S3 event starts
            extract_s3_events(s3_json_event, result)

        # Finally upload the file to destination S3 bucket.
        upload_to_s3(result)
    except ClientError as ex:
        logger.error(str(ex))

        # Send Email notification for all failed S3 event/object
        publish_failed_notification(s3_json_event, ex)
    except Exception as ex:
        logger.error(str(ex))

        # Send Email notification for all failed S3 event/object
        publish_failed_notification(s3_json_event, ex)


def extract_s3_events(s3_json_event, result):
    logger.info("S3 event processing started...")

    try:
        for record in s3_json_event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = unquote_plus(record['s3']['object']['key'])

            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            content = response['Body']
            json_object = content.read().decode('utf-8')

            logger.info("Extracted s3 data: " + json_object)

            consolidate_data(json_object, result)

    except ClientError as ex:
        logger.error(ex)
        raise ex


def consolidate_data(json_object, result):
    logger.info("Consolidation of catalog data is started...")
    partner_map = PartnerDict()

    try:
        catalog_data = json.loads(json_object)

        # Prepare map of Partner Name & Catalog Data
        for catalog in catalog_data:
            partner_map.add(catalog['partner_name'], catalog)

        logger.info("Partner data length: " + str(len(partner_map)))

        for partner in partners_list:
            partner_data = partner_map.get(partner)
            if partner_data is not None:
                logger.info("Partner data for {} is {}".format(partner, partner_data))
                consol_data = prepare_output_data(partner_data)
                result.append(consol_data)
                break

        partner_map = PartnerDict()
    except Exception as ex:
        logger.error(ex)
        raise ex


def fetch_partners_list():
    # Use the DynamoDB client to query partners priority list
    response = dynamodb_client.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='contentType = :contentType',
        ExpressionAttributeValues={
            ':contentType': {'S': 'PriorityList'}
        }
    )
    logger.info(response['Items'])
    logger.info(type(response['Items'][0]['partner_list']['L']))
    for partner in response['Items'][0]['partner_list']['L']:
        partners_list.append(partner['S'])


def upload_to_s3(final_object):
    logger.info("Uploading consolidate data to s3")
    current_time = datetime.datetime.now()

    object_key = 'year=' + str(current_time.year) + '/month=' + str(current_time.month) + '/day=' + str(
        current_time.day) + '/output_object-' + str(current_time.microsecond) + '.jsonl'

    temp_file_name = '/tmp/output_object-' + str(current_time.microsecond) + '.jsonl'
    with open(temp_file_name, 'w') as outfile:
        for entry in final_object:
            json.dump(entry, outfile)
            outfile.write('\n')
    outfile.close()

    try:
        s3_client.upload_file(temp_file_name, DESTINATION_BUCKET, object_key)

    except ClientError as ex:
        logger.error(ex)
        raise ex


def publish_failed_notification(s3_json_event, ex):
    bucket_name = None
    object_key = None

    for record in s3_json_event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = unquote_plus(record['s3']['object']['key'])

    message = prepare_notification_msg(bucket_name, object_key, str(ex))
    sns_client.publish(
        TopicArn=TOPIC_ARN,
        Message=message[1],
        Subject=message[0]
    )


def prepare_output_data(partner_data):
    return {"accommodation_id": partner_data['accommodation_id'],
            "accommodation_data": {"accommodation_name": partner_data['accommodation_data']['accommodation_name']}}


def prepare_notification_msg(source_bucket, source_key, error):
    sub = "Processing Failed"
    msg = """
        Process Failed while consolidating s3 object.
    
        ------------------------------------------------------------------------------------
        Summary of the process:
        ------------------------------------------------------------------------------------
        {a:<20}    :   {source_bucket}
        {b:<22}    :   {source_key}
        {c:<28}    :   {error}
        ------------------------------------------------------------------------------------
        """.format(a='Source Bucket', b='Source Key', c='Error', source_bucket=source_bucket, source_key=source_key,
                   error=error)
    return [sub, msg]
