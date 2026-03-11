# twitter_service.py
"""
Service layer for orchestrating tweet retrieval from the Twitter client.
Handles pagination logic and exports data to local storage for analysis.
"""

import os
import json
import time
from datetime import datetime
from repositories.twitter_client import search_tweets

TWITTER_FILE = "march_2026.json"

def fetch_tweets() -> list:
    """
    Retrieves multiple pages of tweets to ensure a larger data sample.
    
    Args:
        api_key: The authentication key for the Twitter API wrapper.
        
    Returns:
        list: A combined list of tweet objects from all fetched pages.
    """
    all_tweets = []
    seen_tweet_ids = set() 
    cursor = None
    last_min_id = None
    page_count = 0
    
    while True: 
        # Call the API 
        result = search_tweets(cursor=cursor, last_min_id=last_min_id) 

        tweets = result.get("tweets", [])

        if not tweets:  # No more tweets to process
            break

        new_tweets = [tweet for tweet in tweets if tweet.get("id") not in seen_tweet_ids]
        # Add new tweet IDs to the set and tweets to the collection
        all_tweets.extend(new_tweets)
        seen_tweet_ids.update(t.get("id") for t in new_tweets) 

        has_next_page = result.get("has_next_page", False)
        next_cursor  = result.get("next_cursor")

        if next_cursor:
            cursor = next_cursor
            last_min_id = None  # Clear max_id when using cursor
        elif has_next_page and not next_cursor:
            # Fall back to max_id pagination if cursor not available
            last_min_id = tweets[-1].get("id")
            cursor = None
        else:
            break  # No more pagination options

        page_count += 1
        print(f"Fetched page {page_count}, total unique tweets: {len(all_tweets)}, new tweets: {len(new_tweets)}")

        if not new_tweets and not has_next_page:
            print("No new tweets - stopping pagination to save credits")
            break
        
        time.sleep(5) 

    return all_tweets

# TEST MAIN TO CHECK IF SERVICE RETURNS TWEETS CORRECTLY FOR PAGNIATION
if __name__ == "__main__":

    tweets = fetch_tweets()

    print(f"Fetched {len(tweets)} tweets")

    DATA_FOLDER = "data"
    os.makedirs(DATA_FOLDER, exist_ok=True)

    file_path = os.path.join(DATA_FOLDER, TWITTER_FILE)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(tweets, f, indent=2, ensure_ascii=False)
    print(f"Saved tweets to {file_path}")