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
    * CloudWatch Event Rule  
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
* Standard SQS for unlimited throughput
* ReceiveMessageWaitTimeSeconds to reduce empty response from SQS 20s
* 


## Flow-Diagram
![Data Flow Diagram for Lambda Processor](./images/flow-diagram.png)


## Important Links
[Batch-Window feature for AWS lambda & SQS integration](https://aws.amazon.com/about-aws/whats-new/2020/11/aws-lambda-now-supports-batch-windows-of-up-to-5-minutes-for-functions/)