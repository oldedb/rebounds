#!/usr/bin/env python3
"""Test with a known historical date when games definitely existed"""

from nba_api.stats.endpoints import scoreboardv2
from datetime import datetime

# Try a date from last season when we know games existed (Feb 14, 2024 - All-Star related games)
test_date = "2024-02-14"

print(f"Testing with historical date: {test_date}")

try:
    scoreboard = scoreboardv2.ScoreboardV2(game_date=test_date)
    df = scoreboard.get_data_frames()[0]
    print(f"✓ Success! Found {len(df)} games on {test_date}")
    if not df.empty:
        print("\nGames found:")
        for _, row in df.iterrows():
            print(f"  - {row.get('HOME_TEAM_ID')} vs {row.get('VISITOR_TEAM_ID')}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Also try today's date
print(f"\nTesting with today's date: {datetime.now().strftime('%Y-%m-%d')}")
try:
    scoreboard = scoreboardv2.ScoreboardV2(game_date=datetime.now().strftime('%Y-%m-%d'))
    df = scoreboard.get_data_frames()[0]
    print(f"✓ Success! Found {len(df)} games today")
    if df.empty:
        print("  (No games scheduled - this might be normal for today's date)")
except Exception as e:
    print(f"✗ Error: {e}")
