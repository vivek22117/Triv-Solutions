from consolidator.main import *

test_sqs_event = {
    "Records": [{
        'body': '{"Records":[{"eventVersion":"2.1","eventSource":"aws:s3","awsRegion":"us-east-1","eventTime":"2021-02-01T11:07:57.885Z","eventName":"ObjectCreated:Put","userIdentity":{"principalId":"AWS:AROAXORTTGYRSLA4DBARR:vivekm"},"requestParameters":{"sourceIPAddress":"171.50.206.100"},"responseElements":{"x-amz-request-id":"F7266126F7D8431F","x-amz-id-2":"ma3MOcmWSlHVAus7Th5AiaM2PS2uFP3O/6ky09RcyDkaBs/YBFEAJ5y7jpgpsjz5qYcJsyClcuOHAdrE74aB6ij8tWyYrfxA"},"s3":{"s3SchemaVersion":"1.0","configurationId":"trivago-event","bucket":{"name":"trivago-solutions-2021","ownerIdentity":{"principalId":"A3G89N77MCURJW"},"arn":"arn:aws:s3:::trivago-solutions-2021"},"object":{"key":"year%3D2021/month%3D02/day%3D01/data.jsonl","size":463318,"eTag":"f95ac1c0a6ea3b3646191fe8834f4137","sequencer":"006017E111425E971F"}}}]}'
    }]
}


def test_lambda_handler():
    try:
        response = lambda_handler(event=test_sqs_event, context={})
    except Exception as e:
        print(e)
