# parsers/twitter_parser.py
from datetime import datetime
from typing import Dict, List

from utils.json_helpers import create_dict_from_json, save_tweets_to_file

TWEETS_FILE = "merged_tweets.json"


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


def collate_tweets(cleaned_tweets: List[Dict]) -> List[Dict]:
    """for tweets on the same day, make into one master string (with EOT \n
    between them)"""
    collated = {}

    for tweet in cleaned_tweets:
        # Create unique key: (account_name, date)
        key = (tweet["account_name"], tweet["date"])

        if key not in collated:
            # First tweet for this account on this date
            collated[key] = {
                "account_name": tweet["account_name"],
                "date": tweet["date"],
                "master_text": tweet["text"],
            }
        else:
            # Another tweet for same account on same date - append it
            collated[key]["master_text"] += "EOT\n" + tweet["text"]

    return list(collated.values())


if __name__ == "__main__":
    tweets = create_dict_from_json(TWEETS_FILE)
    extracted = extract_metadata(tweets)

    collated = collate_tweets(extracted)
    # save_tweets_to_file(extracted, "data/extracted_tweets.json")
    save_tweets_to_file(collated, "data/processed_tweets.json")
