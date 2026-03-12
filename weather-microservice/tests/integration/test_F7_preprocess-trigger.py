import json
import pytest
from src.lambda_handlers.lambda_handler import collected_lambda_handler

def generate_event(event_name, bucket_name, key, eTag):
    return {
            "Records": [
                {
                "eventSource": "aws:s3",
                "eventName": event_name,
                "s3": {
                    "bucket": {
                    "name": bucket_name
                    },
                    "object": {
                    "key": key,
                    "eTag": eTag
                    }
                }
                }
            ]
        }

def good_test():

    event = generate_event('ObjectCreated:Put', 'clearpath-weather-data', 
                            'weather_collected/3999-12-12.json', 'ckfajs;kf')

    print(collected_lambda_handler(event, None))

def bad_test():
    with open("tests/test_bad_event.json", "r") as f:
        event = json.load(f)

    print(collected_lambda_handler(event, None))

def eTag_test():
    with open("tests/test_eTag_event.json", "r") as f:
        event = json.load(f)

    print(collected_lambda_handler(event, None))

if __name__ == "__main__":
    good_test()