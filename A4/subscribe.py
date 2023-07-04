# Andrew Song - 1204822
# Assignment 4
# CIS4010
# 03/26/23

import boto3
import uuid
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')
        bucket_name = '1204822-subscribe'
        obj = s3.get_object(Bucket=bucket_name, Key="dist_list.txt")
        dist_list = obj['Body'].read().decode('utf-8')

        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        region = event['Records'][0]['awsRegion']
        timestamp = event['Records'][0]['eventTime']
        by = event['Records'][0]['userIdentity']['principalId']

        log = f'Object: {key}\nRegion: {region}\nCreatedDate: {timestamp}\nUser: {by}'
        s3.put_object(Bucket=bucket_name,
                      Key=f'logs/{str(uuid.uuid4())}_log', Body=log)

        buckets = s3.list_buckets()
        for subscriber in dist_list.splitlines():
            bucket_created = False
            for b in buckets["Buckets"]:
                if subscriber in b["Name"]:
                    bucket_created = True
                    s3.copy_object(Bucket=b["Name"], Key=key, CopySource={
                                   "Bucket": bucket, "Key": key})
                    break
            if not bucket_created:
                bucket_name = f"{str(uuid.uuid4())}-{subscriber}"
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': 'ca-central-1'}
                )
                s3.head_bucket(Bucket=bucket_name)
                s3.copy_object(Bucket=bucket_name, Key=key, CopySource={
                            "Bucket": bucket, "Key": key})

    except Exception as err:
        logger.info(err)
        return {
            'statusCode': 400,
            'body': f'Unexpected Error: {err}'
        }

    return {
        'statusCode': 200,
        'body': "Success"
    }
