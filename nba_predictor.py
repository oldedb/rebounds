#!/usr/bin/env python3
"""
NBA Rebound Prediction Module

Analyzes today's NBA matchups and predicts player rebounding performance
based on recent trends and opposing team defensive strength.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import statistics
from dataclasses import dataclass
from nba_api.stats.endpoints import (
    scoreboardv2,
    playergamelogs,
    leaguedashteamstats,
    commonplayerinfo,
    leaguegamefinder
)
from nba_api.stats.static import players, teams
import pandas as pd
import requests
import json


@dataclass
class PlayerPrediction:
    """Represents a rebound prediction for a player"""
    player_name: str
    team: str
    opponent: str
    season_avg_reb: float
    recent_avg_reb: float
    recent_trend: str  # "increasing", "decreasing", "stable"
    opp_def_rating: float
    opp_reb_allowed: float
    opp_pace: float  # Opponent's pace (possessions per 48 min)
    opp_fg_pct: float  # Opponent's FG% allowed (lower = more rebounds)
    opp_fga_per_game: float  # Opponent's shot attempts allowed per game
    prediction: str  # "OVER", "UNDER", "NEUTRAL"
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    reasoning: List[str]


class NBAPredictor:
    """Analyzes NBA games and predicts player rebounding performance"""

    def __init__(self, recent_games: int = 5):
        """
        Initialize the NBA predictor

        Args:
            recent_games: Number of recent games to analyze for trends (default: 5)
        """
        self.recent_games = recent_games
        self.current_season = self._get_current_season()

    def _get_current_season(self) -> str:
        """Get current NBA season string (e.g., '2024-25')"""
        today = datetime.now()
        if today.month >= 10:  # Season starts in October
            return f"{today.year}-{str(today.year + 1)[-2:]}"
        else:
            return f"{today.year - 1}-{str(today.year)[-2:]}"

    def diagnose_api(self) -> None:
        """
        Diagnostic function to check NBA API connectivity and data availability
        Useful for troubleshooting
        """
        print("=" * 60)
        print("NBA API Diagnostics")
        print("=" * 60)

        # Check today's date
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"\n1. Today's Date: {today}")
        print(f"   Current Season: {self.current_season}")

        # Try to fetch scoreboard
        print(f"\n2. Fetching scoreboard for {today}...")
        try:
            scoreboard = scoreboardv2.ScoreboardV2(game_date=today)
            dfs = scoreboard.get_data_frames()
            print(f"   ✓ Success! Found {len(dfs)} DataFrames")

            for i, df in enumerate(dfs):
                print(f"\n   DataFrame {i}:")
                print(f"     - Rows: {len(df)}")
                print(f"     - Columns: {list(df.columns)[:10]}...")  # First 10 columns
                if 'GAME_ID' in df.columns:
                    print(f"     - Contains GAME_ID ✓")
                    print(f"     - Unique games: {df['GAME_ID'].nunique() if not df.empty else 0}")

        except Exception as e:
            print(f"   ✗ Error: {e}")

        # Try to get active players
        print(f"\n3. Testing player data access...")
        try:
            all_players = players.get_active_players()
            print(f"   ✓ Found {len(all_players)} active players")
        except Exception as e:
            print(f"   ✗ Error: {e}")

        # Try to get teams
        print(f"\n4. Testing team data access...")
        try:
            all_teams = teams.get_teams()
            print(f"   ✓ Found {len(all_teams)} teams")
        except Exception as e:
            print(f"   ✗ Error: {e}")

        print("\n" + "=" * 60)

    def get_todays_games(self) -> List[Dict]:
        """
        Fetch today's NBA games using direct HTTP request to bypass library issues

        Returns:
            List of game dictionaries with team information
        """
        try:
            today = datetime.now().strftime('%m/%d/%Y')  # NBA API uses MM/DD/YYYY format

            # Make direct HTTP request to NBA Stats API
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

            print(f"Fetching games for {today}...")
            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                return []

            data = response.json()

            # Navigate to GameHeader result set
            if 'resultSets' not in data:
                print("No resultSets in API response")
                return []

            game_header = None
            for result_set in data['resultSets']:
                if result_set.get('name') == 'GameHeader':
                    game_header = result_set
                    break

            if not game_header:
                print("No GameHeader found in response")
                return []

            headers_list = game_header.get('headers', [])
            rows = game_header.get('rowSet', [])

            if not rows:
                print(f"No games found for {today}")
                return []

            # Find column indices
            try:
                game_id_idx = headers_list.index('GAME_ID')
                home_team_idx = headers_list.index('HOME_TEAM_ID')
                visitor_team_idx = headers_list.index('VISITOR_TEAM_ID')
                status_idx = headers_list.index('GAME_STATUS_TEXT') if 'GAME_STATUS_TEXT' in headers_list else None
            except ValueError as e:
                print(f"Missing required column: {e}")
                print(f"Available columns: {headers_list}")
                return []

            # Parse games
            games = []
            for row in rows:
                try:
                    games.append({
                        'game_id': row[game_id_idx],
                        'home_team': row[home_team_idx],
                        'away_team': row[visitor_team_idx],
                        'game_time': row[status_idx] if status_idx is not None else 'TBD'
                    })
                except (IndexError, TypeError) as e:
                    print(f"Error parsing game row: {e}")
                    continue

            print(f"✓ Found {len(games)} games")
            return games

        except requests.exceptions.RequestException as e:
            print(f"Network error fetching games: {e}")
            return []
        except Exception as e:
            print(f"Error fetching today's games: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return []

    def get_player_recent_stats(self, player_id: int, num_games: int = None) -> pd.DataFrame:
        """
        Get recent game stats for a player

        Args:
            player_id: NBA player ID
            num_games: Number of recent games (defaults to self.recent_games)

        Returns:
            DataFrame with recent game statistics
        """
        if num_games is None:
            num_games = self.recent_games

        try:
            game_logs = playergamelogs.PlayerGameLogs(
                season_nullable=self.current_season,
                player_id_nullable=player_id,
                season_type_nullable='Regular Season'
            )
            df = game_logs.get_data_frames()[0]

            if df.empty:
                return pd.DataFrame()

            # Sort by date and take most recent games
            df = df.sort_values('GAME_DATE', ascending=False).head(num_games)
            return df

        except Exception as e:
            print(f"Error fetching player stats for {player_id}: {e}")
            return pd.DataFrame()

    def get_team_defensive_stats(self, team_id: int) -> Dict:
        """
        Get team's defensive and pace statistics

        Args:
            team_id: NBA team ID

        Returns:
            Dictionary with defensive stats, pace, and shooting percentages
        """
        try:
            team_stats = leaguedashteamstats.LeagueDashTeamStats(
                season=self.current_season,
                season_type_all_star='Regular Season'
            )
            df = team_stats.get_data_frames()[0]

            team_data = df[df['TEAM_ID'] == team_id]

            if team_data.empty:
                return {}

            row = team_data.iloc[0]
            games_played = max(row.get('GP', 1), 1)

            # Calculate opponent FG% (lower = more missed shots = more rebounds)
            opp_fgm = row.get('OPP_FGM', 0)
            opp_fga = row.get('OPP_FGA', 1)
            opp_fg_pct = (opp_fgm / opp_fga * 100) if opp_fga > 0 else 45.0

            # Calculate opponent 3PA per game (more 3s = longer rebounds)
            opp_fg3a = row.get('OPP_FG3A', 0)
            opp_fg3a_per_game = opp_fg3a / games_played

            return {
                'def_rating': row.get('DEF_RATING', 0),
                'opp_reb': row.get('OPP_REB', 0),
                'games_played': games_played,
                'def_reb': row.get('DREB', 0),
                'opp_reb_per_game': row.get('OPP_REB', 0) / games_played,
                'pace': row.get('PACE', 0),  # Possessions per 48 minutes
                'opp_fg_pct': opp_fg_pct,  # Opponent field goal percentage
                'opp_fga_per_game': opp_fga / games_played,  # Opponent shot attempts per game
                'opp_fg3a_per_game': opp_fg3a_per_game,  # Opponent 3PA per game
            }

        except Exception as e:
            print(f"Error fetching team defensive stats: {e}")
            return {}

    def calculate_rebound_trend(self, rebounds: List[float]) -> Tuple[str, float]:
        """
        Calculate rebounding trend from recent games

        Args:
            rebounds: List of rebound totals from recent games (oldest to newest)

        Returns:
            Tuple of (trend_direction, slope)
        """
        if len(rebounds) < 3:
            return "stable", 0.0

        # Simple linear regression slope
        x = list(range(len(rebounds)))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(rebounds)

        numerator = sum((x[i] - x_mean) * (rebounds[i] - y_mean) for i in range(len(rebounds)))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(len(rebounds)))

        if denominator == 0:
            return "stable", 0.0

        slope = numerator / denominator

        # Determine trend
        if slope > 0.5:
            return "increasing", slope
        elif slope < -0.5:
            return "decreasing", slope
        else:
            return "stable", slope

    def predict_player_performance(
        self,
        player_id: int,
        player_name: str,
        team_abbr: str,
        opponent_id: int,
        opponent_abbr: str
    ) -> Optional[PlayerPrediction]:
        """
        Predict if a player will over/under perform their rebound average

        Args:
            player_id: NBA player ID
            player_name: Player's name
            team_abbr: Player's team abbreviation
            opponent_id: Opposing team ID
            opponent_abbr: Opposing team abbreviation

        Returns:
            PlayerPrediction object or None if insufficient data
        """
        # Get player's recent stats
        recent_df = self.get_player_recent_stats(player_id, num_games=self.recent_games)
        season_df = self.get_player_recent_stats(player_id, num_games=50)  # Full season

        if recent_df.empty or season_df.empty:
            return None

        # Calculate averages
        recent_rebounds = recent_df['REB'].tolist()
        recent_avg = statistics.mean(recent_rebounds)
        season_avg = statistics.mean(season_df['REB'].tolist())

        # Skip players with very low rebound numbers (not relevant)
        if season_avg < 3.0:
            return None

        # Calculate trend
        recent_rebounds.reverse()  # Oldest to newest for trend calculation
        trend, slope = self.calculate_rebound_trend(recent_rebounds)

        # Get opponent defensive stats
        opp_def = self.get_team_defensive_stats(opponent_id)

        if not opp_def:
            return None

        # Make prediction
        reasoning = []
        score = 0  # Positive = OVER, Negative = UNDER

        # Factor 1: Recent vs Season Average
        avg_diff = recent_avg - season_avg
        if avg_diff > 1.0:
            score += 2
            reasoning.append(f"Recent avg ({recent_avg:.1f}) significantly above season avg ({season_avg:.1f})")
        elif avg_diff > 0.3:
            score += 1
            reasoning.append(f"Recent avg ({recent_avg:.1f}) above season avg ({season_avg:.1f})")
        elif avg_diff < -1.0:
            score -= 2
            reasoning.append(f"Recent avg ({recent_avg:.1f}) significantly below season avg ({season_avg:.1f})")
        elif avg_diff < -0.3:
            score -= 1
            reasoning.append(f"Recent avg ({recent_avg:.1f}) below season avg ({season_avg:.1f})")

        # Factor 2: Trend
        if trend == "increasing":
            score += 1
            reasoning.append(f"Rebounding trending upward ({slope:.2f} per game)")
        elif trend == "decreasing":
            score -= 1
            reasoning.append(f"Rebounding trending downward ({slope:.2f} per game)")

        # Factor 3: Opponent defensive strength
        # Lower defensive rating = better defense (harder to get rebounds)
        # League average is around 112-114
        opp_def_rating = opp_def.get('def_rating', 113)
        opp_reb_allowed = opp_def.get('opp_reb_per_game', 45)

        if opp_def_rating > 115:
            score += 1
            reasoning.append(f"Opponent has weak defense (rating: {opp_def_rating:.1f})")
        elif opp_def_rating < 108:
            score -= 1
            reasoning.append(f"Opponent has strong defense (rating: {opp_def_rating:.1f})")

        # Factor 4: Rebounds allowed by opponent
        if opp_reb_allowed > 46:
            score += 1
            reasoning.append(f"Opponent allows many rebounds ({opp_reb_allowed:.1f} per game)")
        elif opp_reb_allowed < 42:
            score -= 1
            reasoning.append(f"Opponent limits rebounds ({opp_reb_allowed:.1f} per game)")

        # Factor 5: Pace (more possessions = more rebounding opportunities)
        # League average pace is around 99-101
        opp_pace = opp_def.get('pace', 100)
        if opp_pace > 102:
            score += 1
            reasoning.append(f"High pace game ({opp_pace:.1f} possessions/48min = more opportunities)")
        elif opp_pace < 97:
            score -= 1
            reasoning.append(f"Low pace game ({opp_pace:.1f} possessions/48min = fewer opportunities)")

        # Factor 6: Opponent FG% (lower shooting = more missed shots = more rebounds)
        # League average FG% is around 46-47%
        opp_fg_pct = opp_def.get('opp_fg_pct', 46.5)
        if opp_fg_pct < 44.5:
            score += 1
            reasoning.append(f"Opponent shoots poorly ({opp_fg_pct:.1f}% FG = more missed shots)")
        elif opp_fg_pct > 48.5:
            score -= 1
            reasoning.append(f"Opponent shoots well ({opp_fg_pct:.1f}% FG = fewer missed shots)")

        # Factor 7: Shot volume (more shots = more rebound opportunities)
        opp_fga_per_game = opp_def.get('opp_fga_per_game', 88)
        if opp_fga_per_game > 90:
            score += 1
            reasoning.append(f"High shot volume ({opp_fga_per_game:.1f} FGA/game = more opportunities)")
        elif opp_fga_per_game < 85:
            score -= 1
            reasoning.append(f"Low shot volume ({opp_fga_per_game:.1f} FGA/game = fewer opportunities)")

        # Determine prediction
        if score >= 2:
            prediction = "OVER"
            confidence = "HIGH" if score >= 3 else "MEDIUM"
        elif score <= -2:
            prediction = "UNDER"
            confidence = "HIGH" if score <= -3 else "MEDIUM"
        else:
            prediction = "NEUTRAL"
            confidence = "LOW"

        return PlayerPrediction(
            player_name=player_name,
            team=team_abbr,
            opponent=opponent_abbr,
            season_avg_reb=season_avg,
            recent_avg_reb=recent_avg,
            recent_trend=trend,
            opp_def_rating=opp_def_rating,
            opp_reb_allowed=opp_reb_allowed,
            opp_pace=opp_pace,
            opp_fg_pct=opp_fg_pct,
            opp_fga_per_game=opp_fga_per_game,
            prediction=prediction,
            confidence=confidence,
            reasoning=reasoning
        )

    def get_top_players_by_team(self, team_id: int, top_n: int = 5) -> List[Dict]:
        """
        Get top rebounders from a team

        Args:
            team_id: NBA team ID
            top_n: Number of top players to return

        Returns:
            List of player dictionaries
        """
        try:
            # Get team's recent games to find active players
            game_finder = leaguegamefinder.LeagueGameFinder(
                team_id_nullable=team_id,
                season_nullable=self.current_season,
                season_type_nullable='Regular Season'
            )
            games_df = game_finder.get_data_frames()[0]

            if games_df.empty:
                return []

            # Get unique players and their stats
            # This is a simplified approach - in production you'd want more sophisticated logic
            all_players = players.get_players()
            team_players = [p for p in all_players if p.get('is_active', False)]

            # For simplicity, return a subset
            # In production, you'd query individual player stats to rank them
            return team_players[:top_n]

        except Exception as e:
            print(f"Error getting top players: {e}")
            return []

    def analyze_todays_matchups(self) -> List[PlayerPrediction]:
        """
        Analyze all of today's games and generate predictions

        Returns:
            List of PlayerPrediction objects
        """
        predictions = []

        games = self.get_todays_games()

        if not games:
            print("No games scheduled for today")
            return []

        all_teams = teams.get_teams()
        team_dict = {t['id']: t for t in all_teams}

        for game in games:
            home_id = game['home_team']
            away_id = game['away_team']

            home_team = team_dict.get(home_id, {})
            away_team = team_dict.get(away_id, {})

            # Get top rebounders from both teams
            # Note: This is simplified. In production, you'd have a database
            # of key players or use more sophisticated filtering

            # For demo purposes, we'll use a hardcoded list of star players
            # In production, you'd query this dynamically
            sample_players = self._get_sample_players()

            for player_info in sample_players:
                player_id = player_info['id']
                player_name = player_info['full_name']

                # Determine which team the player plays for
                # This is simplified - you'd need proper roster data
                player_team_id = player_info.get('team_id')

                if player_team_id == home_id:
                    prediction = self.predict_player_performance(
                        player_id,
                        player_name,
                        home_team.get('abbreviation', 'HOME'),
                        away_id,
                        away_team.get('abbreviation', 'AWAY')
                    )
                    if prediction:
                        predictions.append(prediction)

                elif player_team_id == away_id:
                    prediction = self.predict_player_performance(
                        player_id,
                        player_name,
                        away_team.get('abbreviation', 'AWAY'),
                        home_id,
                        home_team.get('abbreviation', 'HOME')
                    )
                    if prediction:
                        predictions.append(prediction)

        return predictions

    def _get_sample_players(self) -> List[Dict]:
        """
        Get a sample of active NBA players
        This is a placeholder - in production you'd use proper roster data

        Returns:
            List of player dictionaries
        """
        all_players = players.get_active_players()

        # Filter for known rebounders (this is just an example)
        # In production, you'd have a more sophisticated selection process
        return all_players[:50]  # Sample of 50 active players


if __name__ == "__main__":
    import sys

    # Check for diagnostic mode
    if len(sys.argv) > 1 and sys.argv[1] == "--diagnose":
        predictor = NBAPredictor(recent_games=5)
        predictor.diagnose_api()
        sys.exit(0)

    # Example usage
    predictor = NBAPredictor(recent_games=5)

    print("Fetching today's NBA games...")
    games = predictor.get_todays_games()

    if not games:
        print("\n⚠️  No games scheduled for today")
        print("\nTroubleshooting tips:")
        print("1. Check if it's the NBA off-season (June - September)")
        print("2. Verify your internet connection")
        print("3. Run diagnostics: python nba_predictor.py --diagnose")
        print("4. Try a specific game date during the season")
    else:
        print(f"\n✓ Found {len(games)} games today")
        print("\nAnalyzing matchups...")

        predictions = predictor.analyze_todays_matchups()

        if predictions:
            print(f"\n{'='*80}")
            print("NBA REBOUND PREDICTIONS")
            print(f"{'='*80}\n")

            for pred in predictions:
                print(f"{pred.player_name} ({pred.team} vs {pred.opponent})")
                print(f"  Season Avg: {pred.season_avg_reb:.1f} | Recent Avg: {pred.recent_avg_reb:.1f}")
                print(f"  Trend: {pred.recent_trend.upper()}")
                print(f"  Prediction: {pred.prediction} ({pred.confidence} confidence)")
                print(f"  Reasoning:")
                for reason in pred.reasoning:
                    print(f"    - {reason}")
                print()
        else:
            print("No predictions generated")
