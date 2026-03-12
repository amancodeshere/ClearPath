from src.repositories.db_repo import get_record
from src.services.weather_attributes import process_collected_s3_object
from pathlib import Path
from datetime import datetime

def collected_lambda_handler(event, context):

    for record in event.get('Records', []):

        event_type = str(record['eventName'])
        if not event_type.startswith("ObjectCreated:"):
            continue
        
        try: 
            key = str(record['s3']['object']['key'])
        except KeyError:
            print("Error in key, skipping object")
            continue

        if not key.startswith('weather_collected/'):
            continue

        date = Path(key).stem

        try:
            bool(datetime.strptime(date, '%Y-%m-%d'))
        except:
            print("Invalid date key format")
            continue

        if get_record(date) is None:
            process_collected_s3_object(key)
            continue
        
        eTag = str(record['s3']['object']['eTag'])
        if eTag != get_record(date)['eTag']:
            process_collected_s3_object(key)
