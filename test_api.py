#!/usr/bin/env python3
"""Test script to debug NBA API calls"""

import requests
from datetime import datetime

# Get today's date in NBA API format
today = datetime.now().strftime('%m/%d/%Y')
print(f"Testing NBA API for date: {today}")

# NBA Stats API endpoint
url = "https://stats.nba.com/stats/scoreboardv2"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.nba.com/',
    'Origin': 'https://www.nba.com',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true'
}

params = {
    'GameDate': today,
    'LeagueID': '00',
    'DayOffset': '0'
}

print(f"\nURL: {url}")
print(f"Headers: {headers}")
print(f"Params: {params}")

try:
    response = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Response Length: {len(response.text)} chars")
    print(f"\nFirst 500 chars of response:")
    print(response.text[:500])

    if response.status_code == 200:
        try:
            data = response.json()
            print("\n✓ Valid JSON response")
            print(f"Keys in response: {list(data.keys())}")
        except Exception as e:
            print(f"\n✗ JSON parsing error: {e}")
    else:
        print(f"\n✗ HTTP Error: {response.status_code}")

except Exception as e:
    print(f"\n✗ Request failed: {e}")
