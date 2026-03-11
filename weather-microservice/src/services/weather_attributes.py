from src.dependencies.s3_client import s3_client, S3_BUCKET_NAME
from src.repositories.s3_repo import read_file
from src.repositories.db_repo import get_record
import urllib.parse

def process_collected_s3_object(key: str):

    if not key.startswith('weather_collected/'):
        return False
    
    content = read_file(key)
    print(content)

    if not get_record(key):
        print('h')

    return True