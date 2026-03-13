# twitter_client.py
"""
Twitter API client for retrieving Sydney Trains disruption alerts.
Part of the alert-microservice for the ClearPath project.
Credits:
    Initial implementation adapted from the TwitterAPI.io Advanced Search
    documentation: https://twitterapi.io/blog/scrape-twitter-history-tweet
"""
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TWITTER_API_KEY")
# The endpoint for advanced search provided by the third-party Twitter API
# wrapper.
BASE_URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"

# Search query focusing on T1 Sydney Trains account for specific disruption
# keywords.
# Excludes retweets to minimize duplicate alert data.

# Base query (without dates)

class TwitterClient: 
    """client for collected queries from external API"""

    BASE_QUERY = (
        "(from:T1SydneyTrains) "
        "(delay OR disruption OR cancelled OR suspended "
        "OR delayed OR allow extra time)"
    )

    def __init__(self, api_url, api_key, max_retries: int = 3):
        self.api_url = BASE_URL
        self.api_key = api_key or os.getenv("TWITTER_API_KEY")
        self.headers = {"X-API-Key": api_key} 
        self.max_retries = max_retries

    def search_tweets_by_query(query: str) -> list:
        """
        Fetches the latest tweets matching the transit disruption query.

        Args:
            query: updated query with dates for each week

        Returns:
            dict: The JSON response containing tweet data and pagination metadata.

        Raises:
            requests.exceptions.HTTPError: If the API request fails
            (e.g., 401 Unauthorized).
        """

        headers = {"x-api-key": API_KEY}
        all_tweets = []
        seen_ids = set()
        cursor = None
        max_retries = 3

        while True:
            # use max_id to retrive older tweet beyond pagination
            params = {"query": query, "queryType": "Top"}

            if cursor:
                params["cursor"] = cursor

            retry_count = 0

            while retry_count < max_retries:
                try:
                    # Perform the GET request to the advanced search endpoint
                    response = requests.get(
                        BASE_URL, headers=headers, params=params
                    )
                    response.raise_for_status()
                    data = response.json()

                    tweets = data.get("tweets", [])
                    has_next = data.get("has_next_page", False)
                    cursor = data.get("next_cursor", None)

                    # Deduplicate tweets
                    new_tweets = []
                    for t in tweets:
                        tid = t.get("id")
                        if tid not in seen_ids:
                            seen_ids.add(tid)
                            new_tweets.append(t)
                            all_tweets.append(t)

                    print(
                        f"API returned {len(tweets)} tweets, "
                        f"{len(new_tweets)} new, "
                        f"total: {len(all_tweets)}"
                    )

                    if not has_next:
                        return all_tweets

                    break

                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    print(f"  Error: {e}, retry {retry_count}/{max_retries}")

                    time.sleep(2**retry_count)
                    if retry_count == max_retries:
                        print("Max retries reached, returning collected tweets")
                        return all_tweets

            if not has_next:
                break

        return all_tweets

