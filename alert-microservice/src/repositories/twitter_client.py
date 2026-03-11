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
QUERY = "(from:T1SydneyTrains) (delay OR disruption OR cancelled OR suspended OR delayed OR allow extra time) until:2026-03-11 since:2026-03-01"

def search_tweets(cursor: str = None, last_min_id: str = None) -> dict:
    """
    Fetches the latest tweets matching the transit disruption query.

    Args:
        last_min_id: the ID of the last tweet returned by cursor to allow retrival of historic data beyond the twitter api limits 
        cursor: A pagination token used to retrieve the next page of search results.

    Returns:
        dict: The JSON response containing tweet data and pagination metadata.

    Raises:
        requests.exceptions.HTTPError: If the API request fails (e.g., 401 Unauthorized).
    """

    headers = {"x-api-key": API_KEY}
    #use max_id to retrive older tweet beyond pagination 
    params = {
        "query": QUERY,
        "queryType": "Latest"
    }

    if cursor:
        params["cursor"] = cursor
    elif last_min_id:
        params["query"] = f"{QUERY} max_id:{last_min_id}"
        

    # Perform the GET request to the advanced search endpoint
    response = requests.get(BASE_URL, headers=headers, params=params)

    # Automatically raises an exception for 4xx or 5xx status codes
    response.raise_for_status()
    
    return response.json()