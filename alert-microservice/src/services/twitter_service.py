# twitter_service.py
"""
Service layer for orchestrating tweet retrieval from the Twitter client.
Handles pagination logic and exports data to local storage for analysis.
"""

import json
import os
import time
from datetime import datetime, timedelta

from repositories.twitter_client import BASE_QUERY, search_tweets_by_query

TWEETS_FILE = "tweets_jan_feb_2025.json"
# Date range to fetch
START_DATE = datetime.strptime("2025-01-01", "%Y-%m-%d")
END_DATE = datetime.strptime("2025-02-28", "%Y-%m-%d")


def generate_weekly_queries(start_date: datetime, end_date: datetime):
    """
    Generate weekly query ranges from start_date to end_date.
    Each query covers 7 days.
    """
    queries = []
    current = start_date

    while current < end_date:
        next_week = current + timedelta(days=7)

        if next_week > end_date:
            next_week = end_date

        q = f"{BASE_QUERY} since:{current.strftime('%Y-%m-%d')} until:{next_week.strftime('%Y-%m-%d')}"

        queries.append(q)
        current = next_week

    return queries


def fetch_tweets() -> list:
    """
    Retrieves multiple pages of tweets to ensure a larger data sample.

    Args:
        api_key: The authentication key for the Twitter API wrapper.

    Returns:
        list: A combined list of tweet objects from all fetched pages.
    """

    DATA_FOLDER = "data"
    os.makedirs(DATA_FOLDER, exist_ok=True)
    file_path = os.path.join(DATA_FOLDER, TWEETS_FILE)

    all_tweets = []

    print(
        f"\nFetching tweets from {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}"
    )
    queries = generate_weekly_queries(START_DATE, END_DATE)
    print(f"Generated {len(queries)} weekly queries\n")

    for i, q in enumerate(queries, 1):
        # Extract dates from query for display
        date_range = q.split("since:")[1].split(" until:")
        print(f"[{i}/{len(queries)}] Week: {date_range[0]} to {date_range[1]}")

        # Fetch tweets for this week
        week_tweets = search_tweets_by_query(q)
        all_tweets.extend(week_tweets)
        print(f"  Collected {len(week_tweets)} tweets\n")

        # Be polite to the API
        time.sleep(1)

    unique_tweets = list({t["id"]: t for t in all_tweets}.values())
    print(f"Total unique tweets: {len(unique_tweets)}")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(unique_tweets, f, indent=2, ensure_ascii=False)

    print(f"Saved to {TWEETS_FILE}")

    return unique_tweets


# TEST MAIN TO CHECK IF SERVICE RETURNS TWEETS CORRECTLY FOR PAGNIATION
if __name__ == "__main__":

    tweets = fetch_tweets()

    print(f"Fetched {len(tweets)} tweets")
