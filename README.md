# How to execute the component

> To test the code you should have AWS account with full access. Follow below steps to create
>multiple resources required for testing.


* Create 2 S3 buckets
    * Source Bucket: <Source Datata Bucket> 
    * Destination Bucket: partners-consolidated-data
* Create SQS to queue s3 put events
    * Configure SQS Access policy to source S3 bucket
* Configure event notification on source s3 bucket with destination as SQS
* Create dynamodb table to hold list of priority partners.
    * Name: Partners-Priority-Storage
    * PartitionKey: contentType (String Type)
    * Insert Dummy data using below command
    ```
      aws dynamodb put-item --table-name Partners-Priority-Storage \
      --item file://<PATH TO JSON FILE>
      --region us-east-1
      --profile <AWS Profile OR Default>
    ```
    *  Json file attached is added in the zip for dynamoDB data.
* Create IAM role for AWS lambda to access S3 bucket, DynamoDB table, SNS, SQS, cloudwatch log
    * Configure trigger for SQS with Batch size 10 and Batch Window of 120s
    * Upload code main.py file and press deploy.
    * Upload dummy file in source bucket.