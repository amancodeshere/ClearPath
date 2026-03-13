"""
DynamoDB client initialisation and connection testing. s
"""

import os

import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = "clearpath-weather-data"

# Initialise DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

# Reference your table
alert_table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def check_table_status() -> bool:
    try:
        _ = alert_table.table_status
        print(f"DynamoDB connected: {DYNAMODB_TABLE_NAME}")
        return True
    except Exception as e:
        print(f"DynamoDB connection failed: {e}")
        return False


if __name__ == "__main__":
    check_table_status()
