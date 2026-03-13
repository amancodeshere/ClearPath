# parsers/twitter_parser.py
import os
import json
from collections import defaultdict
from datetime import datetime

TWEETS_FILE = os.path.join("data", "merged_tweets.json")

# Take all the data created by the FR18 and merge into one JSON file 


# Extract only the date and account name etc 

def create_dict_from_json (file_path: str) -> dict: 
    with open(file_path, 'r') as f:
        tweets = json.load(f)  
    return tweets

def format_date(created_at: str):
    try:
        date_obj = datetime.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
        date_formatted = date_obj.strftime('%Y-%m-%d')
    except:
        date_formatted = 'Invalid Date'
    
    return date_formatted

def extract_metadata (tweets: dict): 
    """
    
    args - takes the converted dict of tweets 
    returns - returns dic of 
    text, createdAt, author.name 

    """

    extracted_tweets = []

    for tweet in tweets:

        extracted_tweets.append({
            'account_name': tweet.get('author', {}).get('name', 'Unknown'),
            'date': format_date(tweet.get('createdAt')),
            'text': tweet.get('text', '')
        })

    return extracted_tweets

if __name__ == "__main__":
    print("this is nothing main")