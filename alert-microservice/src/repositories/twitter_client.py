# twitter_client.py
"""
Twitter API client for retrieving Sydney Trains disruption alerts.
Part of the alert-microservice for the ClearPath project.
Credits:
    Initial implementation adapted from the TwitterAPI.io Advanced Search 
    documentation: https://twitterapi.io/blog/scrape-twitter-history-tweet
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TWITTER_API_KEY")
# The endpoint for advanced search provided by the third-party Twitter API wrapper.
BASE_URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"

# Search query focusing on T1 Sydney Trains account for specific disruption keywords.
# Excludes retweets to minimize duplicate alert data. 

# Base query (without dates)
BASE_QUERY = "(from:T1SydneyTrains) (delay OR disruption OR cancelled OR suspended OR delayed OR allow extra time)"

# File where the data will be output 
JSON_FILE = "historical_t1_tweets.json"


def search_tweets_by_query(query: str) -> list:
    """
    Fetches the latest tweets matching the transit disruption query.

    Args:
        query: updated query with dates for each week 

    Returns:
        dict: The JSON response containing tweet data and pagination metadata.

    Raises:
        requests.exceptions.HTTPError: If the API request fails (e.g., 401 Unauthorized).
    """

    headers = {"x-api-key": API_KEY}
    all_tweets = []
    seen_ids = set()
    cursor = None
    max_retries = 3

    while True: 
    #use max_id to retrive older tweet beyond pagination 
        params = {
            "query": query,
            "queryType": "Latest"
        }

        if cursor:
            params["cursor"] = cursor

        retry_count = 0

        while retry_count < max_retries:
            try:
                # Perform the GET request to the advanced search endpoint
                response = requests.get(BASE_URL, headers=headers, params=params)
            except requests.exceptions.RequestException as e:
                # Automatically raises an exception for 4xx or 5xx status codes
                response.raise_for_status()
    
    return response.json()