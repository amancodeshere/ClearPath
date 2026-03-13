"""
S3 client initialisation and connection testing.s
"""

import os

import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
S3_BUCKET_NAME = "clearpath-weather-data"

# Initialise S3 client
s3_client = boto3.client("s3", region_name=AWS_REGION)


def check_bucket_status() -> bool:
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        print(f"S3 connected: {S3_BUCKET_NAME}")
        return True
    except Exception as e:
        print(f"S3 connection failed: {e}")
        return False


if __name__ == "__main__":
    check_bucket_status()
