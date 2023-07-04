# Andrew Song - 1204822
# Assignment 4
# CIS4010
# 03/26/23

import boto3
import os

def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')
        
        bucket = event['queryStringParameters']['bucket']
        file = event['queryStringParameters']['filename']
    
        response = s3.get_object(Bucket=bucket, Key=file)
        body = response['Body'].read()
    
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': f'attachment; filename="{file}"'
        }
    
        return {
             'statusCode': 200,
             'body': body,
             'headers': headers
        }
    except Exception as err:
        return {
            'statusCode': 400,
            'body': err + " please fix request and try again."
        }