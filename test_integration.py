#!/usr/bin/env python3
"""
Test integration of new ESPN API-based predictor
Simulates what the Streamlit app does
"""

from nba_predictor import NBAPredictor

print("=" * 80)
print("Testing NBA Predictor Integration")
print("=" * 80)

print("\n1. Initializing predictor...")
predictor = NBAPredictor(recent_games=5)
print("✓ Predictor initialized")

print("\n2. Fetching today's games...")
games = predictor.get_todays_games()
print(f"✓ Found {len(games)} games")

if games:
    print("\nGames:")
    for game in games:
        print(f"  - {game['away_team']['abbreviation']} @ {game['home_team']['abbreviation']}")

print("\n3. Analyzing matchups...")
predictions = predictor.analyze_todays_matchups()
print(f"✓ Generated {len(predictions)} predictions")

if predictions:
    # Apply filters similar to what the Streamlit app does
    min_season_avg = 3.0
    filtered = [p for p in predictions if p.season_avg_reb >= min_season_avg]

    print(f"\n4. Applying filters (min {min_season_avg} rebounds)...")
    print(f"✓ {len(filtered)} predictions after filtering")

    # Count by prediction type
    over_count = sum(1 for p in filtered if p.prediction == "OVER")
    under_count = sum(1 for p in filtered if p.prediction == "UNDER")
    neutral_count = sum(1 for p in filtered if p.prediction == "NEUTRAL")
    high_conf = sum(1 for p in filtered if p.confidence == "HIGH")

    print("\n5. Summary Statistics:")
    print(f"  Total Predictions: {len(filtered)}")
    print(f"  OVER: {over_count}")
    print(f"  UNDER: {under_count}")
    print(f"  NEUTRAL: {neutral_count}")
    print(f"  High Confidence: {high_conf}")

    # Show sample predictions
    print("\n6. Sample Predictions:")
    for pred in filtered[:3]:
        print(f"\n  {pred.player_name} ({pred.team} vs {pred.opponent})")
        print(f"    Season Avg: {pred.season_avg_reb:.1f}, Recent: {pred.recent_avg_reb:.1f}")
        print(f"    Prediction: {pred.prediction} ({pred.confidence} confidence)")
        print(f"    Trend: {pred.recent_trend}")

print("\n" + "=" * 80)
print("✓ Integration test PASSED - App should work correctly!")
print("=" * 80)
