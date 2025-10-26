#!/usr/bin/env python3
"""
ESPN API Wrapper for NBA Data

This module provides a clean interface to ESPN's NBA API for fetching
game schedules, team stats, and player information.

ESPN API Documentation (unofficial):
- Scoreboard: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard
- Teams: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams
- Team details: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{id}
"""

import requests
from datetime import datetime
from typing import List, Dict, Optional
import os


class ESPNNBAClient:
    """Client for accessing ESPN's NBA API"""

    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"

    def __init__(self, use_mock_data: bool = False, override_date: Optional[str] = None):
        """
        Initialize ESPN NBA API client

        Args:
            use_mock_data: If True, use mock data instead of making API calls
            override_date: Override system date (format: YYYY-MM-DD). If None, uses system date.
        """
        self.use_mock_data = use_mock_data or os.environ.get('USE_MOCK_DATA') == 'true'
        self.override_date = override_date or os.environ.get('NBA_DATE_OVERRIDE')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.espn.com/',
        }

        if self.override_date:
            print(f"📅 Using date override: {self.override_date}")

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make HTTP request to ESPN API

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response as dictionary or None if request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"ESPN API Error: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Error making request: {e}")
            return None

    def get_todays_games(self) -> List[Dict]:
        """
        Get today's NBA games

        Returns:
            List of game dictionaries with structure:
            {
                'game_id': str,
                'home_team': {'id': str, 'name': str, 'abbreviation': str},
                'away_team': {'id': str, 'name': str, 'abbreviation': str},
                'game_time': str,
                'status': str
            }
        """
        if self.use_mock_data:
            return self._get_mock_todays_games()

        # Build parameters with date override if specified
        params = {}
        if self.override_date:
            # ESPN API expects date in YYYYMMDD format
            date_formatted = self.override_date.replace('-', '')
            params['dates'] = date_formatted

        data = self._make_request("scoreboard", params=params)

        if not data:
            return []

        games = []
        events = data.get('events', [])

        for event in events:
            try:
                game_id = event.get('id')
                status = event.get('status', {}).get('type', {}).get('description', 'Scheduled')

                competitions = event.get('competitions', [])
                if not competitions:
                    continue

                comp = competitions[0]
                competitors = comp.get('competitors', [])

                if len(competitors) < 2:
                    continue

                # Find home and away teams
                home_team = next((c for c in competitors if c.get('homeAway') == 'home'), None)
                away_team = next((c for c in competitors if c.get('homeAway') == 'away'), None)

                if not home_team or not away_team:
                    continue

                games.append({
                    'game_id': game_id,
                    'home_team': {
                        'id': home_team.get('team', {}).get('id'),
                        'name': home_team.get('team', {}).get('displayName'),
                        'abbreviation': home_team.get('team', {}).get('abbreviation'),
                    },
                    'away_team': {
                        'id': away_team.get('team', {}).get('id'),
                        'name': away_team.get('team', {}).get('displayName'),
                        'abbreviation': away_team.get('team', {}).get('abbreviation'),
                    },
                    'game_time': event.get('date'),
                    'status': status
                })

            except Exception as e:
                print(f"Error parsing game: {e}")
                continue

        return games

    def get_all_teams(self) -> List[Dict]:
        """
        Get all NBA teams

        Returns:
            List of team dictionaries
        """
        if self.use_mock_data:
            return self._get_mock_teams()

        data = self._make_request("teams")

        if not data:
            return []

        teams = []
        sports = data.get('sports', [])

        if sports:
            leagues = sports[0].get('leagues', [])
            if leagues:
                team_data = leagues[0].get('teams', [])
                for item in team_data:
                    team = item.get('team', {})
                    teams.append({
                        'id': team.get('id'),
                        'name': team.get('displayName'),
                        'abbreviation': team.get('abbreviation'),
                        'location': team.get('location'),
                        'nickname': team.get('name'),
                    })

        return teams

    def get_team_stats(self, team_id: str) -> Optional[Dict]:
        """
        Get team statistics

        Args:
            team_id: ESPN team ID

        Returns:
            Dictionary with team stats or None
        """
        if self.use_mock_data:
            return self._get_mock_team_stats(team_id)

        data = self._make_request(f"teams/{team_id}")

        if not data:
            return None

        team = data.get('team', {})

        # Extract relevant statistics
        # Note: ESPN's team endpoint structure varies, adjust as needed
        return {
            'id': team.get('id'),
            'name': team.get('displayName'),
            'record': team.get('record', {}),
            # Additional stats can be added when available
        }

    def _get_mock_todays_games(self) -> List[Dict]:
        """Return mock game data for testing"""
        return [
            {
                'game_id': '401584901',
                'home_team': {
                    'id': '5',
                    'name': 'Los Angeles Lakers',
                    'abbreviation': 'LAL',
                },
                'away_team': {
                    'id': '16',
                    'name': 'Phoenix Suns',
                    'abbreviation': 'PHX',
                },
                'game_time': datetime.now().isoformat(),
                'status': 'Scheduled'
            },
            {
                'game_id': '401584902',
                'home_team': {
                    'id': '2',
                    'name': 'Boston Celtics',
                    'abbreviation': 'BOS',
                },
                'away_team': {
                    'id': '20',
                    'name': 'Miami Heat',
                    'abbreviation': 'MIA',
                },
                'game_time': datetime.now().isoformat(),
                'status': 'Scheduled'
            },
            {
                'game_id': '401584903',
                'home_team': {
                    'id': '9',
                    'name': 'Golden State Warriors',
                    'abbreviation': 'GSW',
                },
                'away_team': {
                    'id': '13',
                    'name': 'Denver Nuggets',
                    'abbreviation': 'DEN',
                },
                'game_time': datetime.now().isoformat(),
                'status': 'Scheduled'
            },
        ]

    def _get_mock_teams(self) -> List[Dict]:
        """Return mock team data"""
        return [
            {'id': '1', 'name': 'Atlanta Hawks', 'abbreviation': 'ATL', 'location': 'Atlanta', 'nickname': 'Hawks'},
            {'id': '2', 'name': 'Boston Celtics', 'abbreviation': 'BOS', 'location': 'Boston', 'nickname': 'Celtics'},
            {'id': '3', 'name': 'Brooklyn Nets', 'abbreviation': 'BKN', 'location': 'Brooklyn', 'nickname': 'Nets'},
            {'id': '4', 'name': 'Charlotte Hornets', 'abbreviation': 'CHA', 'location': 'Charlotte', 'nickname': 'Hornets'},
            {'id': '5', 'name': 'Chicago Bulls', 'abbreviation': 'CHI', 'location': 'Chicago', 'nickname': 'Bulls'},
            {'id': '6', 'name': 'Cleveland Cavaliers', 'abbreviation': 'CLE', 'location': 'Cleveland', 'nickname': 'Cavaliers'},
            {'id': '7', 'name': 'Dallas Mavericks', 'abbreviation': 'DAL', 'location': 'Dallas', 'nickname': 'Mavericks'},
            {'id': '8', 'name': 'Denver Nuggets', 'abbreviation': 'DEN', 'location': 'Denver', 'nickname': 'Nuggets'},
            {'id': '9', 'name': 'Detroit Pistons', 'abbreviation': 'DET', 'location': 'Detroit', 'nickname': 'Pistons'},
            {'id': '10', 'name': 'Golden State Warriors', 'abbreviation': 'GSW', 'location': 'Golden State', 'nickname': 'Warriors'},
            {'id': '11', 'name': 'Houston Rockets', 'abbreviation': 'HOU', 'location': 'Houston', 'nickname': 'Rockets'},
            {'id': '12', 'name': 'Indiana Pacers', 'abbreviation': 'IND', 'location': 'Indiana', 'nickname': 'Pacers'},
            {'id': '13', 'name': 'LA Clippers', 'abbreviation': 'LAC', 'location': 'LA', 'nickname': 'Clippers'},
            {'id': '14', 'name': 'Los Angeles Lakers', 'abbreviation': 'LAL', 'location': 'Los Angeles', 'nickname': 'Lakers'},
            {'id': '15', 'name': 'Memphis Grizzlies', 'abbreviation': 'MEM', 'location': 'Memphis', 'nickname': 'Grizzlies'},
            {'id': '16', 'name': 'Miami Heat', 'abbreviation': 'MIA', 'location': 'Miami', 'nickname': 'Heat'},
            {'id': '17', 'name': 'Milwaukee Bucks', 'abbreviation': 'MIL', 'location': 'Milwaukee', 'nickname': 'Bucks'},
            {'id': '18', 'name': 'Minnesota Timberwolves', 'abbreviation': 'MIN', 'location': 'Minnesota', 'nickname': 'Timberwolves'},
            {'id': '19', 'name': 'New Orleans Pelicans', 'abbreviation': 'NOP', 'location': 'New Orleans', 'nickname': 'Pelicans'},
            {'id': '20', 'name': 'New York Knicks', 'abbreviation': 'NYK', 'location': 'New York', 'nickname': 'Knicks'},
            {'id': '21', 'name': 'Oklahoma City Thunder', 'abbreviation': 'OKC', 'location': 'Oklahoma City', 'nickname': 'Thunder'},
            {'id': '22', 'name': 'Orlando Magic', 'abbreviation': 'ORL', 'location': 'Orlando', 'nickname': 'Magic'},
            {'id': '23', 'name': 'Philadelphia 76ers', 'abbreviation': 'PHI', 'location': 'Philadelphia', 'nickname': '76ers'},
            {'id': '24', 'name': 'Phoenix Suns', 'abbreviation': 'PHX', 'location': 'Phoenix', 'nickname': 'Suns'},
            {'id': '25', 'name': 'Portland Trail Blazers', 'abbreviation': 'POR', 'location': 'Portland', 'nickname': 'Trail Blazers'},
            {'id': '26', 'name': 'Sacramento Kings', 'abbreviation': 'SAC', 'location': 'Sacramento', 'nickname': 'Kings'},
            {'id': '27', 'name': 'San Antonio Spurs', 'abbreviation': 'SAS', 'location': 'San Antonio', 'nickname': 'Spurs'},
            {'id': '28', 'name': 'Toronto Raptors', 'abbreviation': 'TOR', 'location': 'Toronto', 'nickname': 'Raptors'},
            {'id': '29', 'name': 'Utah Jazz', 'abbreviation': 'UTA', 'location': 'Utah', 'nickname': 'Jazz'},
            {'id': '30', 'name': 'Washington Wizards', 'abbreviation': 'WAS', 'location': 'Washington', 'nickname': 'Wizards'},
        ]

    def _get_mock_team_stats(self, team_id: str) -> Dict:
        """Return mock team stats"""
        return {
            'id': team_id,
            'name': 'Mock Team',
            'defensive_rating': 112.5,
            'rebounds_allowed_per_game': 44.5,
            'pace': 100.2,
            'opp_fg_pct': 46.3,
            'opp_fga_per_game': 88.5,
        }


if __name__ == "__main__":
    # Test the ESPN API client
    print("Testing ESPN NBA API Client")
    print("=" * 60)

    # Try without mock data first
    client = ESPNNBAClient(use_mock_data=False)

    print("\n1. Fetching today's games...")
    games = client.get_todays_games()

    if games:
        print(f"✓ Found {len(games)} games")
        for game in games:
            print(f"  {game['away_team']['abbreviation']} @ {game['home_team']['abbreviation']}")
    else:
        print("⚠️ No games found or API unavailable - switching to mock data")
        client.use_mock_data = True
        games = client.get_todays_games()
        print(f"✓ Using {len(games)} mock games")
        for game in games:
            print(f"  {game['away_team']['abbreviation']} @ {game['home_team']['abbreviation']}")

    print("\n2. Fetching teams...")
    teams = client.get_all_teams()
    print(f"✓ Found {len(teams)} teams")
    for team in teams[:5]:
        print(f"  {team['abbreviation']}: {team['name']}")
