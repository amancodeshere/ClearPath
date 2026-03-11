import boto3
from src.dependencies.s3_client import s3_client
from src.repositories.db_repo import get_record
from src.services.weather_attributes import process_collected_s3_object
from pathlib import Path

def collected_lambda_handler(event, context):

    for record in event.get('Records', []):

        event_type = str(record['eventName'])
        if not event_type == "ObjectCreated:Put":
            continue

        key = str(record['s3']['object']['key'])
        if not key.startswith('weather_collected/'):
            continue

        rec_path = Path(key)
        date = rec_path.stem
        if get_record(date):
            continue

        process_collected_s3_object(key)
