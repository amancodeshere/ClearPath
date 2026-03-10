# twitter_client.py

import requests

BASE_URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"

QUERY = "from:T1SydneyTrains (delay OR disruption OR cancelled OR suspended OR delayed) -filter:retweets"

def search_tweets(api_key: str, cursor: str = "") -> dict:
    headers = {"x-api-key": api_key}
    params = {"query": QUERY, "queryType": "Latest", "cursor": cursor}
    
    response = requests.get(BASE_URL, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()