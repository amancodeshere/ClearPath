# parsers/twitter_parser.py
import json
import os
from datetime import datetime

TWEETS_FILE = os.path.join("data", "merged_tweets.json")


def create_dict_from_json(file_path: str) -> dict:
    """
    Load tweets from JSON file and return as dictionary.

    Args:
        file_path (str): Path to the JSON file containing tweets

    Returns:
        dict: Dictionary/list of tweet objects from the JSON file
    """
    with open(file_path, "r") as f:
        tweets = json.load(f)
    return tweets


def format_date(created_at: str):
    """
    Parse Twitter date format and convert to YYYY-MM-DD.

    Args:
        created_at (str): Date string in Twitter format
        "Fri Nov 07 22:02:37 +0000 2025"

    Returns:
        str: Formatted date as YYYY-MM-DD, or 'Invalid Date' if parsing fails
    """
    try:
        date_obj = datetime.strptime(created_at, "%a %b %d %H:%M:%S +0000 %Y")
        date_formatted = date_obj.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        date_formatted = "Invalid Date"

    return date_formatted


def extract_metadata(tweets: dict):
    """
    Extract only essential metadata from tweets.

    Retains only: account_name, date (YYYY-MM-DD), text
    Removes all other metadata (likes, retweets, IDs, etc.)

    Args:
        tweets (dict): Dictionary of tweet objects from JSON

    Returns:
        list: List of dictionaries with account_name, date, and text fields
    """

    extracted_tweets = []

    for tweet in tweets:
        extracted_tweets.append(
            {
                "account_name": tweet.get("author", {}).get("name", "Unknown"),
                "date": format_date(tweet.get("createdAt")),
                "text": tweet.get("text", ""),
            }
        )

    return extracted_tweets


def save_tweets_to_file(tweets: list, output_file: str) -> None:
    """Save tweets to JSON file"""
    with open(output_file, "w") as f:
        json.dump(tweets, f, indent=2)
    print(f"Saved {len(tweets)} tweets to {output_file}")


if __name__ == "__main__":

    tweets = create_dict_from_json(TWEETS_FILE)
    extracted = extract_metadata(tweets)

    save_tweets_to_file(extracted, "data/extracted_tweets.json")
