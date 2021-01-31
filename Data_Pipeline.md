## Data Pipeline design for Accommodation Consolidator.

## Table of contents
* [General info](#general-info)
* [Technologies & AWS Services](#technologies)
* [Flow-Diagram](#flow-diagram)


## General info
Accommodation Consolidator project is designed to process and consolidate the partners catalog data using multiple AWS resources. The
input raw data is going to be S3 bucket and after consolidation the output destination is also S3 bucket.
This documents take you through the complete data pipeline desing i.e. reading from s3, processing components & final storage.


## Technologies & AWS Services
* Python3.X
* Terraform for IAC (Infrastructure as Code)
* Jenkins for Automation of Infra and Code Deployment
* AWS Resources:
    * S3 Bucket
    * SQS
    * AWS DynamoDB
    * AWS Lambda
    * AWS CloudWatch
    * AWS IAM
    

## AWS Resource Configuration

Source S3 Bucket
***
> Source S3 bucket will receive partner's catalog data in the form of jsonl files.
> We can configure s3 event notification for all created/put object api calls with destination as SQS.


SQS
***
> SQS will act as the interface between consolidator and the raw data received in S3 bucket.
> For each new record in s3 a SQS event will be pushed in SQS.
* SQS Access policy to allow S3 to publish events
* Standard SQS for unlimited throughput
* ReceiveMessageWaitTimeSeconds to reduce empty response from SQS 20s
* Configure DLQ to store all erroneous and throttled messages
* MaxReceiveCount of 10, so that throttled message will eventually get processed.
* VisibilityTimeout should be approx 450s as out lambda is configured with 90s


AWS DynamoDB
***
> AWS DynamoDB to store list of priority partners.
* Configure sufficient amount of ReadCapacity along with 2 write capacity is sufficient.


AWS Lambda
***
> AWS lambda to execute consolidator script.
* Triggered configured with SQS.
* Batch Size of 10 (Configurable to 10,000 as per latest updates)
* Batch Window of 120s so that lambda wait to poll messages from SQS


AWS CloudWatch
***
> AWS CloudWatch to store lambda logs, metric to track lambda error, IteratorAge & SQS
ApproximateAgeOfOldestMessage to identify how fast is queue being processed.


AWS IAM
***
> AWS IAM role to have granular access to other services from AWS lambda.

## Flow-Diagram
![Data Flow Diagram for Lambda Processor](./data/images/data_flow_diagram.jpg)


## Important Links
[Batch-Window feature for AWS lambda & SQS integration](https://aws.amazon.com/about-aws/whats-new/2020/11/aws-lambda-now-supports-batch-windows-of-up-to-5-minutes-for-functions/)