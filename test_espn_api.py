#!/usr/bin/env python3
"""Test ESPN API to understand data structure"""

import requests
import json
from datetime import datetime

# Better headers to avoid blocking
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.espn.com/',
    'Origin': 'https://www.espn.com',
}

print("=" * 80)
print("Testing ESPN NBA API")
print("=" * 80)

# Test 1: Get today's scoreboard
print("\n1. Testing Scoreboard Endpoint")
url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success!")
        print(f"\nTop-level keys: {list(data.keys())}")

        events = data.get('events', [])
        print(f"\nNumber of games today: {len(events)}")

        if events:
            print("\n--- Sample Game Data ---")
            game = events[0]
            print(f"Game ID: {game.get('id')}")
            print(f"Name: {game.get('name')}")
            print(f"Short Name: {game.get('shortName')}")
            print(f"Date: {game.get('date')}")
            print(f"Status: {game.get('status', {}).get('type', {}).get('description')}")

            competitions = game.get('competitions', [])
            if competitions:
                comp = competitions[0]
                competitors = comp.get('competitors', [])
                print(f"\nTeams:")
                for team_data in competitors:
                    team = team_data.get('team', {})
                    print(f"  - {team.get('displayName')} (ID: {team.get('id')})")
                    print(f"    Abbreviation: {team.get('abbreviation')}")

            # Save sample for inspection
            with open('espn_game_sample.json', 'w') as f:
                json.dump(game, f, indent=2)
            print("\n✓ Saved sample game data to espn_game_sample.json")
        else:
            print("\n⚠️ No games today, but API is working!")
            print("This is normal - today might not have any NBA games scheduled.")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Response: {response.text[:200]}")

except Exception as e:
    print(f"✗ Exception: {e}")

# Test 2: Get teams
print("\n\n2. Testing Teams Endpoint")
teams_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"

try:
    response = requests.get(teams_url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
        print(f"✓ Found {len(teams)} teams")

        if teams:
            print("\nSample teams:")
            for i in range(min(3, len(teams))):
                team_data = teams[i].get('team', {})
                print(f"  {i+1}. {team_data.get('displayName')} (ID: {team_data.get('id')}, Abbr: {team_data.get('abbreviation')})")

            # Save for reference
            with open('espn_teams.json', 'w') as f:
                json.dump(teams[:5], f, indent=2)
            print("\n✓ Saved sample teams to espn_teams.json")
    else:
        print(f"✗ Error: {response.status_code}")

except Exception as e:
    print(f"✗ Exception: {e}")

# Test 3: Try a historical date with known games
print("\n\n3. Testing Scoreboard with Historical Date (2024-02-14)")
hist_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates=20240214"

try:
    response = requests.get(hist_url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        events = data.get('events', [])
        print(f"✓ Found {len(events)} games on 2024-02-14")

        if events:
            print("Games found:")
            for event in events[:3]:
                print(f"  - {event.get('shortName')}")
    else:
        print(f"✗ Error: {response.status_code}")

except Exception as e:
    print(f"✗ Exception: {e}")

print("\n" + "=" * 80)
print("ESPN API Test Complete")
print("=" * 80)
