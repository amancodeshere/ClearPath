import json
from src.lambda_handlers.lambda_handler import collected_lambda_handler


def good_test():
    with open("tests/test_good_event.json", "r") as f:
        event = json.load(f)

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
    bad_test()
    eTag_test()