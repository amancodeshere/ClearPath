import json
import os


def create_dict_from_json(filename: str) -> dict:
    """
    Load tweets from JSON file and return as dictionary.

    Args:
        filename (str): JSON file containing tweets (in data/)

    Returns:
        dict: Dictionary/list of tweet objects from the JSON file
    """
    current_file = os.path.abspath(__file__)
    utils_dir = os.path.dirname(current_file)
    src_dir = os.path.dirname(utils_dir)
    file_path = os.path.join(src_dir, "data", filename)

    with open(file_path, "r") as f:
        tweets = json.load(f)
    return tweets


def save_tweets_to_file(tweets: list, output_file: str) -> None:
    """Save tweets to JSON file"""
    with open(output_file, "w") as f:
        json.dump(tweets, f, indent=2)
    print(f"Saved {len(tweets)} tweets to {output_file}")
