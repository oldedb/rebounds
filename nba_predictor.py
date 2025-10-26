#!/usr/bin/env python3
"""
NBA Rebound Prediction Module - ESPN API Version

Analyzes today's NBA matchups and predicts player rebounding performance
based on recent trends and opposing team defensive strength.

This version uses ESPN API (with mock data fallback) instead of NBA Stats API.
"""

from datetime import datetime
from typing import List, Dict, Tuple, Optional
import statistics
from dataclasses import dataclass
import os

# Import our new ESPN API client and mock data
from espn_api import ESPNNBAClient
from mock_nba_data import (
    generate_recent_game_stats,
    get_mock_player_by_team,
    get_mock_team_stats,
    get_all_mock_players
)


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

    def __init__(self, recent_games: int = 5, use_mock_data: bool = None, override_date: str = None):
        """
        Initialize the NBA predictor

        Args:
            recent_games: Number of recent games to analyze for trends (default: 5)
            use_mock_data: If True, use mock data. If None, auto-detect based on environment
            override_date: Override system date (format: YYYY-MM-DD). Useful when system clock is wrong.
        """
        self.recent_games = recent_games
        self.current_season = self._get_current_season()
        self.override_date = override_date or os.environ.get('NBA_DATE_OVERRIDE')

        # Auto-enable mock data in restricted environments or if explicitly requested
        if use_mock_data is None:
            self.use_mock_data = os.environ.get('USE_MOCK_DATA', 'true').lower() == 'true'
        else:
            self.use_mock_data = use_mock_data

        # Initialize ESPN API client
        self.espn_client = ESPNNBAClient(use_mock_data=self.use_mock_data, override_date=self.override_date)

        if self.use_mock_data:
            print("ℹ️  Running in MOCK DATA mode for testing")

    def _get_current_season(self) -> str:
        """Get current NBA season string (e.g., '2024-25')"""
        today = datetime.now()
        if today.month >= 10:  # Season starts in October
            return f"{today.year}-{str(today.year + 1)[-2:]}"
        else:
            return f"{today.year - 1}-{str(today.year)[-2:]}"

    def get_todays_games(self) -> List[Dict]:
        """
        Fetch today's NBA games

        Returns:
            List of game dictionaries with team information
        """
        games = self.espn_client.get_todays_games()

        if not games and not self.use_mock_data:
            print("⚠️  No games from API, switching to mock data")
            self.use_mock_data = True
            self.espn_client.use_mock_data = True
            games = self.espn_client.get_todays_games()

        return games

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
        player: Dict,
        opponent_id: str,
        opponent_abbr: str
    ) -> Optional[PlayerPrediction]:
        """
        Predict if a player will over/under perform their rebound average

        Args:
            player: Player dictionary with stats
            opponent_id: Opposing team ID
            opponent_abbr: Opposing team abbreviation

        Returns:
            PlayerPrediction object or None if insufficient data
        """
        player_name = player['name']
        team_abbr = player['team_abbr']
        season_avg = player['season_avg_reb']

        # Skip players with very low rebound numbers (not relevant)
        if season_avg < 3.0:
            return None

        # Get recent game stats
        recent_games = generate_recent_game_stats(player['id'], num_games=self.recent_games)

        if not recent_games:
            return None

        # Calculate recent average
        recent_rebounds = [game['rebounds'] for game in recent_games]
        recent_avg = statistics.mean(recent_rebounds)

        # Calculate trend (oldest to newest)
        trend, slope = self.calculate_rebound_trend(recent_rebounds)

        # Get opponent defensive stats
        opp_stats = get_mock_team_stats(opponent_id)

        opp_def_rating = opp_stats.get('defensive_rating', 112.0)
        opp_reb_allowed = opp_stats.get('rebounds_allowed_per_game', 44.5)
        opp_pace = opp_stats.get('pace', 100.0)
        opp_fg_pct = opp_stats.get('opp_fg_pct', 46.0)
        opp_fga_per_game = opp_stats.get('opp_fga_per_game', 88.0)

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

        # Factor 5: Pace
        if opp_pace > 102:
            score += 1
            reasoning.append(f"High pace game ({opp_pace:.1f} possessions/48min = more opportunities)")
        elif opp_pace < 97:
            score -= 1
            reasoning.append(f"Low pace game ({opp_pace:.1f} possessions/48min = fewer opportunities)")

        # Factor 6: Opponent FG%
        if opp_fg_pct < 44.5:
            score += 1
            reasoning.append(f"Opponent shoots poorly ({opp_fg_pct:.1f}% FG = more missed shots)")
        elif opp_fg_pct > 48.5:
            score -= 1
            reasoning.append(f"Opponent shoots well ({opp_fg_pct:.1f}% FG = fewer missed shots)")

        # Factor 7: Shot volume
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

        print(f"Analyzing {len(games)} games...")

        for game in games:
            home_id = game['home_team']['id']
            away_id = game['away_team']['id']
            home_abbr = game['home_team']['abbreviation']
            away_abbr = game['away_team']['abbreviation']

            # Get players for both teams
            home_players = get_mock_player_by_team(home_id)
            away_players = get_mock_player_by_team(away_id)

            # Analyze home team players
            for player in home_players:
                prediction = self.predict_player_performance(player, away_id, away_abbr)
                if prediction:
                    predictions.append(prediction)

            # Analyze away team players
            for player in away_players:
                prediction = self.predict_player_performance(player, home_id, home_abbr)
                if prediction:
                    predictions.append(prediction)

        print(f"Generated {len(predictions)} predictions")
        return predictions


if __name__ == "__main__":
    import sys

    # Example usage
    predictor = NBAPredictor(recent_games=5)

    print("Fetching today's NBA games...")
    games = predictor.get_todays_games()

    if not games:
        print("\n⚠️  No games scheduled for today")
    else:
        print(f"\n✓ Found {len(games)} games today")
        for game in games:
            print(f"  {game['away_team']['abbreviation']} @ {game['home_team']['abbreviation']}")

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
