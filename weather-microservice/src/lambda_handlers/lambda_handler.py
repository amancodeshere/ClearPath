from src.repositories.db_repo import get_record
from src.services.weather_attributes import process_collected_s3_object
from src.dependencies.s3_client import S3_BUCKET_NAME
from pathlib import Path
from datetime import datetime

def collected_lambda_handler(event, context):

    for record in event.get('Records', []):

        bucket = str(record['s3']['bucket']['name'])
        if bucket != S3_BUCKET_NAME:
            continue

        event_type = str(record['eventName'])
        if not event_type.startswith("ObjectCreated:"):
            continue
        
        try: 
            key = str(record['s3']['object']['key'])
        except KeyError:
            print("Key cannot be found in record, skipping object")
            continue

        if not key.startswith('weather_collected/'):
            continue

        date = Path(key).stem
        try:
            bool(datetime.strptime(date, '%Y-%m-%d'))
        except:
            print("Invalid date key format")
            continue

        eTag = str(record['s3']['object']['eTag'])
        if get_record(date) is None:
            print('hi')
            process_collected_s3_object(key, eTag)
            continue
        
        if eTag != get_record(date)['eTag']:
            print('hi')
            process_collected_s3_object(key, eTag)

