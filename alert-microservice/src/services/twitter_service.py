# twitter_service.py
"""
Service layer for orchestrating tweet retrieval from the Twitter client.
Handles pagination logic and exports data to local storage for analysis.
"""

import json
import time
from repositories.twitter_client import search_tweets


def fetch_tweets(api_key: str) -> list:
    """
    Retrieves multiple pages of tweets to ensure a larger data sample.
    
    Args:
        api_key: The authentication key for the Twitter API wrapper.
        
    Returns:
        list: A combined list of tweet objects from all fetched pages.
    """
    all_tweets = []

    # page 1
    result = search_tweets(api_key=api_key)
    all_tweets.extend(result.get("tweets", []))
    cursor = result.get("next_cursor")

    # Respect rate limits for the API provider (1 request per 5s for free tier)
    time.sleep(5) 

    # page 2
    result2 = search_tweets(api_key=api_key, cursor=cursor)
    all_tweets.extend(result2.get("tweets", []))

    return all_tweets


# TEST MAIN TO CHECK IF SERVICE RETURNS TWEETS CORRECTLY FOR PAGNIATION
if __name__ == "__main__":
    API_KEY = "new1_15db99e37b744832b97ded2c5531c417"

    tweets = fetch_tweets(api_key=API_KEY)

    print(f"Fetched {len(tweets)} tweets")

with open("sample_tweets.json", "w") as f:
    json.dump(tweets, f, indent=2)