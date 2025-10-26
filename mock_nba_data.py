#!/usr/bin/env python3
"""
Mock NBA Data for Testing

This module provides realistic mock data for testing the NBA predictor
when real API access is unavailable.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict

# Mock player roster with realistic rebound averages
MOCK_PLAYERS = [
    # Lakers
    {'id': 1, 'name': 'Anthony Davis', 'team_id': '14', 'team_abbr': 'LAL', 'season_avg_reb': 12.5, 'position': 'PF-C'},
    {'id': 2, 'name': 'LeBron James', 'team_id': '14', 'team_abbr': 'LAL', 'season_avg_reb': 7.2, 'position': 'SF'},
    {'id': 3, 'name': 'Rui Hachimura', 'team_id': '14', 'team_abbr': 'LAL', 'season_avg_reb': 4.8, 'position': 'PF'},

    # Suns
    {'id': 4, 'name': 'Devin Booker', 'team_id': '24', 'team_abbr': 'PHX', 'season_avg_reb': 4.5, 'position': 'SG'},
    {'id': 5, 'name': 'Kevin Durant', 'team_id': '24', 'team_abbr': 'PHX', 'season_avg_reb': 6.7, 'position': 'PF'},
    {'id': 6, 'name': 'Jusuf Nurkić', 'team_id': '24', 'team_abbr': 'PHX', 'season_avg_reb': 10.3, 'position': 'C'},

    # Celtics
    {'id': 7, 'name': 'Jayson Tatum', 'team_id': '2', 'team_abbr': 'BOS', 'season_avg_reb': 8.4, 'position': 'PF'},
    {'id': 8, 'name': 'Jaylen Brown', 'team_id': '2', 'team_abbr': 'BOS', 'season_avg_reb': 5.9, 'position': 'SG-SF'},
    {'id': 9, 'name': 'Kristaps Porziņģis', 'team_id': '2', 'team_abbr': 'BOS', 'season_avg_reb': 7.8, 'position': 'PF-C'},
    {'id': 10, 'name': 'Al Horford', 'team_id': '2', 'team_abbr': 'BOS', 'season_avg_reb': 6.5, 'position': 'C'},

    # Heat
    {'id': 11, 'name': 'Bam Adebayo', 'team_id': '16', 'team_abbr': 'MIA', 'season_avg_reb': 10.4, 'position': 'C'},
    {'id': 12, 'name': 'Jimmy Butler', 'team_id': '16', 'team_abbr': 'MIA', 'season_avg_reb': 5.3, 'position': 'SF'},
    {'id': 13, 'name': 'Tyler Herro', 'team_id': '16', 'team_abbr': 'MIA', 'season_avg_reb': 5.4, 'position': 'SG'},

    # Warriors
    {'id': 14, 'name': 'Stephen Curry', 'team_id': '10', 'team_abbr': 'GSW', 'season_avg_reb': 4.5, 'position': 'PG'},
    {'id': 15, 'name': 'Draymond Green', 'team_id': '10', 'team_abbr': 'GSW', 'season_avg_reb': 7.2, 'position': 'PF'},
    {'id': 16, 'name': 'Kevon Looney', 'team_id': '10', 'team_abbr': 'GSW', 'season_avg_reb': 7.8, 'position': 'C'},

    # Nuggets
    {'id': 17, 'name': 'Nikola Jokić', 'team_id': '8', 'team_abbr': 'DEN', 'season_avg_reb': 12.4, 'position': 'C'},
    {'id': 18, 'name': 'Aaron Gordon', 'team_id': '8', 'team_abbr': 'DEN', 'season_avg_reb': 6.5, 'position': 'PF'},
    {'id': 19, 'name': 'Michael Porter Jr.', 'team_id': '8', 'team_abbr': 'DEN', 'season_avg_reb': 7.1, 'position': 'SF'},
]

# Team defensive stats (ESPN team IDs as strings)
MOCK_TEAM_STATS = {
    '14': {  # Lakers
        'defensive_rating': 111.2,
        'rebounds_allowed_per_game': 43.5,
        'pace': 101.3,
        'opp_fg_pct': 46.2,
        'opp_fga_per_game': 87.3,
    },
    '24': {  # Suns
        'defensive_rating': 113.8,
        'rebounds_allowed_per_game': 45.7,
        'pace': 99.8,
        'opp_fg_pct': 47.1,
        'opp_fga_per_game': 89.2,
    },
    '2': {  # Celtics
        'defensive_rating': 109.5,
        'rebounds_allowed_per_game': 42.1,
        'pace': 98.2,
        'opp_fg_pct': 44.8,
        'opp_fga_per_game': 85.6,
    },
    '16': {  # Heat
        'defensive_rating': 110.7,
        'rebounds_allowed_per_game': 44.2,
        'pace': 97.5,
        'opp_fg_pct': 45.5,
        'opp_fga_per_game': 86.8,
    },
    '10': {  # Warriors
        'defensive_rating': 115.2,
        'rebounds_allowed_per_game': 46.3,
        'pace': 102.1,
        'opp_fg_pct': 47.8,
        'opp_fga_per_game': 91.2,
    },
    '8': {  # Nuggets
        'defensive_rating': 112.3,
        'rebounds_allowed_per_game': 44.8,
        'pace': 100.5,
        'opp_fg_pct': 46.5,
        'opp_fga_per_game': 88.7,
    },
}


def generate_recent_game_stats(player_id: int, num_games: int = 5) -> List[Dict]:
    """
    Generate mock recent game statistics for a player

    Args:
        player_id: Player ID
        num_games: Number of recent games to generate

    Returns:
        List of game stat dictionaries
    """
    player = next((p for p in MOCK_PLAYERS if p['id'] == player_id), None)

    if not player:
        return []

    season_avg = player['season_avg_reb']
    games = []

    # Generate games with some variance around season average
    for i in range(num_games):
        # Add some randomness: ±30% of season average
        variance = random.uniform(-0.3, 0.3) * season_avg
        rebounds = max(0, int(season_avg + variance))

        game_date = datetime.now() - timedelta(days=(num_games - i) * 2)

        games.append({
            'game_id': f'mock_game_{player_id}_{i}',
            'game_date': game_date.strftime('%Y-%m-%d'),
            'player_id': player_id,
            'player_name': player['name'],
            'rebounds': rebounds,
            'points': int(random.uniform(15, 30)),
            'assists': int(random.uniform(2, 8)),
            'minutes': int(random.uniform(28, 38)),
        })

    return games


def get_mock_player_by_team(team_id: str) -> List[Dict]:
    """
    Get mock players for a specific team

    Args:
        team_id: ESPN team ID

    Returns:
        List of player dictionaries
    """
    return [p for p in MOCK_PLAYERS if p['team_id'] == team_id]


def get_mock_team_stats(team_id: str) -> Dict:
    """
    Get mock team defensive statistics

    Args:
        team_id: ESPN team ID

    Returns:
        Dictionary with team stats
    """
    return MOCK_TEAM_STATS.get(team_id, {
        'defensive_rating': 112.0,
        'rebounds_allowed_per_game': 44.5,
        'pace': 100.0,
        'opp_fg_pct': 46.0,
        'opp_fga_per_game': 88.0,
    })


def get_all_mock_players() -> List[Dict]:
    """Get all mock players"""
    return MOCK_PLAYERS.copy()


if __name__ == "__main__":
    # Test mock data generation
    print("Testing Mock NBA Data")
    print("=" * 60)

    print("\n1. All Mock Players:")
    for player in MOCK_PLAYERS[:5]:
        print(f"  {player['name']} ({player['team_abbr']}) - {player['season_avg_reb']} reb/game")

    print("\n2. Recent Game Stats for Anthony Davis:")
    ad_stats = generate_recent_game_stats(1, num_games=5)
    for game in ad_stats:
        print(f"  {game['game_date']}: {game['rebounds']} rebounds")

    print("\n3. Lakers Players:")
    lakers = get_mock_player_by_team('14')
    for player in lakers:
        print(f"  {player['name']} - {player['season_avg_reb']} reb/game")

    print("\n4. Suns Team Stats:")
    suns_stats = get_mock_team_stats('24')
    print(f"  Defensive Rating: {suns_stats['defensive_rating']}")
    print(f"  Rebounds Allowed: {suns_stats['rebounds_allowed_per_game']}")
    print(f"  Pace: {suns_stats['pace']}")
