# twitter_client.py
"""
Twitter API client for retrieving Sydney Trains disruption alerts.
Part of the alert-microservice for the ClearPath project.
Credits:
    Initial implementation adapted from the TwitterAPI.io Advanced Search 
    documentation: https://twitterapi.io/blog/scrape-twitter-history-tweet
"""

import requests

# The endpoint for advanced search provided by the third-party Twitter API wrapper.
BASE_URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"

# Search query focusing on T1 Sydney Trains account for specific disruption keywords.
# Excludes retweets to minimize duplicate alert data. 
QUERY = "from:T1SydneyTrains (delay OR disruption OR cancelled OR suspended OR delayed) -filter:retweets"

def search_tweets(api_key: str, cursor: str = "") -> dict:
    """
    Fetches the latest tweets matching the transit disruption query.

    Args:
        api_key: The x-api-key required for authenticating with the Twitter API provider.
        cursor: A pagination token used to retrieve the next page of search results.

    Returns:
        dict: The JSON response containing tweet data and pagination metadata.

    Raises:
        requests.exceptions.HTTPError: If the API request fails (e.g., 401 Unauthorized).
    """

    headers = {"x-api-key": api_key}
    params = {"query": QUERY, "queryType": "Latest", "cursor": cursor}
    
    # Perform the GET request to the advanced search endpoint
    response = requests.get(BASE_URL, headers=headers, params=params)

    # Automatically raises an exception for 4xx or 5xx status codes
    response.raise_for_status()
    
    return response.json()