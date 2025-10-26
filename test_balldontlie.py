#!/usr/bin/env python3
"""Test balldontlie.io API - Free NBA data for developers"""

import requests
import json
from datetime import datetime, timedelta

print("=" * 80)
print("Testing balldontlie.io NBA API")
print("=" * 80)

# balldontlie.io is a free public API specifically for developers
BASE_URL = "https://www.balldontlie.io/api/v1"

# Test 1: Get all teams
print("\n1. Testing Teams Endpoint")
url = f"{BASE_URL}/teams"

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        teams = data.get('data', [])
        print(f"✓ Success! Found {len(teams)} teams")

        if teams:
            print("\nSample teams:")
            for team in teams[:5]:
                print(f"  {team.get('id')}. {team.get('full_name')} ({team.get('abbreviation')})")

            # Save for reference
            with open('balldontlie_teams.json', 'w') as f:
                json.dump(teams, f, indent=2)
            print("\n✓ Saved teams to balldontlie_teams.json")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Response: {response.text[:200]}")

except Exception as e:
    print(f"✗ Exception: {e}")

# Test 2: Get games for today
print("\n\n2. Testing Games Endpoint (Today)")
today = datetime.now().strftime('%Y-%m-%d')
url = f"{BASE_URL}/games?dates[]={today}"

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        games = data.get('data', [])
        print(f"✓ Success! Found {len(games)} games for {today}")

        if games:
            print("\nGames today:")
            for game in games:
                home = game.get('home_team', {})
                visitor = game.get('visitor_team', {})
                print(f"  {visitor.get('abbreviation')} @ {home.get('abbreviation')}")
                print(f"    Status: {game.get('status')}")
        else:
            print("  No games scheduled for today")
    else:
        print(f"✗ Error: {response.status_code}")

except Exception as e:
    print(f"✗ Exception: {e}")

# Test 3: Get games for a known historical date
print("\n\n3. Testing Games Endpoint (Historical - 2024-02-14)")
hist_date = "2024-02-14"
url = f"{BASE_URL}/games?dates[]={hist_date}"

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        games = data.get('data', [])
        print(f"✓ Success! Found {len(games)} games for {hist_date}")

        if games:
            print("\nSample games:")
            for game in games[:3]:
                home = game.get('home_team', {})
                visitor = game.get('visitor_team', {})
                home_score = game.get('home_team_score', 0)
                visitor_score = game.get('visitor_team_score', 0)
                print(f"  {visitor.get('abbreviation')} {visitor_score} @ {home.get('abbreviation')} {home_score}")

            # Save sample
            with open('balldontlie_game_sample.json', 'w') as f:
                json.dump(games[0], f, indent=2)
            print("\n✓ Saved sample game to balldontlie_game_sample.json")
    else:
        print(f"✗ Error: {response.status_code}")

except Exception as e:
    print(f"✗ Exception: {e}")

# Test 4: Get player stats
print("\n\n4. Testing Players Endpoint")
url = f"{BASE_URL}/players?per_page=5"

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        players = data.get('data', [])
        print(f"✓ Success! Found {len(players)} players (showing first page)")

        if players:
            print("\nSample players:")
            for player in players[:5]:
                print(f"  {player.get('id')}. {player.get('first_name')} {player.get('last_name')} - {player.get('team', {}).get('abbreviation', 'N/A')}")
    else:
        print(f"✗ Error: {response.status_code}")

except Exception as e:
    print(f"✗ Exception: {e}")

# Test 5: Get season averages for a player
print("\n\n5. Testing Season Averages Endpoint")
# Using LeBron James (ID: 237)
url = f"{BASE_URL}/season_averages?season=2023&player_ids[]=237"

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        stats = data.get('data', [])
        print(f"✓ Success! Found stats")

        if stats:
            player_stats = stats[0]
            print(f"\nSample season averages:")
            print(f"  Games: {player_stats.get('games_played')}")
            print(f"  Points: {player_stats.get('pts')}")
            print(f"  Rebounds: {player_stats.get('reb')}")
            print(f"  Assists: {player_stats.get('ast')}")

            # Save sample
            with open('balldontlie_stats_sample.json', 'w') as f:
                json.dump(player_stats, f, indent=2)
            print("\n✓ Saved sample stats to balldontlie_stats_sample.json")
    else:
        print(f"✗ Error: {response.status_code}")

except Exception as e:
    print(f"✗ Exception: {e}")

print("\n" + "=" * 80)
print("balldontlie.io API Test Complete")
print("=" * 80)
print("\nNote: balldontlie.io is a free API designed for developers.")
print("It provides historical data but may have delays for live games.")
