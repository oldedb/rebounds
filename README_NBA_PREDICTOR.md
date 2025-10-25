# NBA Rebound Predictor

An intelligent NBA analytics tool that predicts player rebounding performance based on recent trends and defensive matchup analysis.

## Overview

The NBA Rebound Predictor analyzes today's NBA matchups and identifies players who are likely to **over-perform** or **under-perform** their season rebounding averages. It combines multiple factors including:

- Recent performance trends (hot/cold streaks)
- Statistical trajectory (increasing/decreasing patterns)
- Opposing team defensive strength
- **Game pace and tempo** (possessions per game)
- **Shooting efficiency** (missed shots = rebound opportunities)
- **Shot volume** (total shot attempts)
- Historical rebounding data

## Features

- **Real-time Game Analysis**: Automatically fetches today's NBA schedule
- **Advanced Multi-factor Predictions**: Combines **7 statistical factors** for each prediction
- **Pace & Tempo Analysis**: Considers game speed and possession count
- **Shooting Analytics**: Evaluates opponent FG% and shot volume for rebound opportunities
- **Confidence Ratings**: HIGH/MEDIUM/LOW confidence levels
- **Interactive Dashboard**: Beautiful Streamlit UI with charts and visualizations
- **Trend Analysis**: Identifies players on hot or cold streaks
- **Defensive Matchups**: Considers opponent's defensive rating and rebounding metrics
- **Export Functionality**: Download predictions as CSV for further analysis

## Installation

### Requirements

- Python 3.8+
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd oldedb
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Web App

Launch the Streamlit web interface:

```bash
streamlit run nba_app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Command Line Module

You can also use the predictor as a Python module:

```python
from nba_predictor import NBAPredictor

# Initialize predictor
predictor = NBAPredictor(recent_games=5)

# Get today's games
games = predictor.get_todays_games()

# Analyze matchups
predictions = predictor.analyze_todays_matchups()

# Display predictions
for pred in predictions:
    print(f"{pred.player_name}: {pred.prediction} ({pred.confidence})")
```

### Running from Command Line

```bash
python nba_predictor.py
```

## How It Works

### Prediction Algorithm

The predictor uses a multi-factor scoring system with **7 key factors**:

#### Factor 1: Recent vs Season Average (±2 points)
- Recent avg significantly above season avg: +2
- Recent avg above season avg: +1
- Recent avg below season avg: -1
- Recent avg significantly below season avg: -2

#### Factor 2: Trend Analysis (±1 point)
- Increasing trend: +1
- Decreasing trend: -1
- Stable trend: 0

#### Factor 3: Opponent Defensive Rating (±1 point)
- Weak defense (>115 rating): +1
- Strong defense (<108 rating): -1
- Average defense: 0

#### Factor 4: Rebounds Allowed (±1 point)
- High rebounds allowed (>46/game): +1
- Low rebounds allowed (<42/game): -1
- Average: 0

#### Factor 5: Pace (±1 point) **NEW**
- High pace (>102 poss/48min): +1
- Low pace (<97 poss/48min): -1
- Average pace: 0

**Why it matters**: More possessions = more shots = more rebound opportunities

#### Factor 6: Opponent Field Goal % (±1 point) **NEW**
- Poor shooting (<44.5% FG): +1
- Good shooting (>48.5% FG): -1
- Average shooting: 0

**Why it matters**: Lower shooting percentage = more missed shots = more rebounds available

#### Factor 7: Shot Volume (±1 point) **NEW**
- High volume (>90 FGA/game): +1
- Low volume (<85 FGA/game): -1
- Average volume: 0

**Why it matters**: More shot attempts = more total rebound opportunities

### Final Prediction

**Score ≥ +2**: OVER (HIGH confidence if ≥ +3)
**Score ≤ -2**: UNDER (HIGH confidence if ≤ -3)
**Score between -1 and +1**: NEUTRAL (LOW confidence)

With 7 factors, the maximum possible score is +7 (all factors positive) or -7 (all factors negative)

### Trend Calculation

Uses linear regression on recent games to calculate slope:
- **Slope > 0.5**: Increasing trend
- **Slope < -0.5**: Decreasing trend
- **-0.5 ≤ Slope ≤ 0.5**: Stable

## Web Interface Guide

### Sidebar Controls

1. **Recent Games to Analyze**: Number of recent games to consider (3-10)
2. **Minimum Season Rebound Average**: Filter out low-volume rebounders
3. **Show Neutral Predictions**: Include/exclude neutral predictions
4. **Analyze Today's Games**: Run the analysis

### Main Tabs

#### 1. Predictions Tab
- View all player predictions
- Filter by prediction type (OVER/UNDER/NEUTRAL)
- Filter by confidence level
- Expand for detailed analysis and reasoning

#### 2. Analytics Tab
- Prediction distribution (pie chart)
- Confidence distribution (bar chart)
- Recent vs Season average scatter plot
- Complete data table with all metrics
- CSV export functionality

#### 3. About Tab
- Detailed methodology explanation
- Best practices
- Tool limitations

## Configuration

### Adjustable Parameters

In the Streamlit sidebar:
- **Recent Games**: 3-10 games (default: 5)
- **Minimum Rebounds**: 1-8 rebounds/game (default: 3)
- **Show Neutral**: Toggle to include/exclude neutral predictions

In the code (`nba_predictor.py`):
- Prediction thresholds (lines 248-257)
- Trend slope sensitivity (line 204)
- Defensive rating thresholds (lines 260-265)

## Example Output

```
NBA REBOUND PREDICTIONS
================================================================================

Nikola Jokic (DEN vs LAL)
  Season Avg: 12.4 | Recent Avg: 14.2
  Trend: INCREASING
  Prediction: OVER (HIGH confidence)
  Reasoning:
    - Recent avg (14.2) significantly above season avg (12.4)
    - Rebounding trending upward (0.78 per game)
    - Opponent allows many rebounds (47.2 per game)

Anthony Davis (LAL vs DEN)
  Season Avg: 11.8 | Recent Avg: 9.6
  Trend: DECREASING
  Prediction: UNDER (MEDIUM confidence)
  Reasoning:
    - Recent avg (9.6) below season avg (11.8)
    - Rebounding trending downward (-0.62 per game)
```

## Data Source

This tool uses the **nba_api** Python package, which provides access to:
- NBA official statistics
- Real-time game schedules
- Player game logs
- Team statistics
- Historical data

**Note**: This is an unofficial API. Rate limits and availability may vary.

## Best Practices

### For Optimal Results

1. **Run on Game Days**: The tool needs active NBA games to generate predictions
2. **Focus on High Confidence**: Pay attention to predictions with HIGH confidence
3. **Consider Context**: Check for injuries, rest days, and lineup changes
4. **Track Results**: Download CSV files to track prediction accuracy over time
5. **Adjust Parameters**: Experiment with recent game windows for your use case

### Interpretation Tips

- **OVER with HIGH confidence**: Strong matchup, player in good form
- **UNDER with HIGH confidence**: Tough matchup, player struggling
- **Look for convergence**: Multiple factors pointing same direction
- **Increasing trends**: Players getting hot, momentum building
- **Weak opponent defense**: More rebounding opportunities

## Limitations

- **No injury data**: Does not account for player injuries or rest
- **No lineup changes**: Doesn't track starting/bench status changes
- **Historical only**: Past performance doesn't guarantee future results
- **Simplified model**: Real NBA games have many complex factors
- **API dependencies**: Requires nba_api to be functional
- **Entertainment use**: Not intended for professional betting advice

## Troubleshooting

### Common Issues

**"No games scheduled for today"**
- The NBA season may be in off-season or All-Star break
- Try running on a regular season game day

**"Error fetching player stats"**
- API rate limit may be reached
- Network connectivity issues
- Try again in a few minutes

**Missing predictions**
- Player may not meet minimum rebound threshold
- Insufficient game history (early season)
- Data not available from API

**Slow performance**
- Analyzing many players takes time
- First run caches data (subsequent runs faster)
- Reduce number of recent games analyzed

## Contributing

This is a research/entertainment tool. Improvements welcome:
- Enhanced prediction algorithms
- Additional statistical factors
- Better player filtering
- Injury data integration
- Machine learning models

## Technical Architecture

```
nba_predictor.py
├── NBAPredictor class
│   ├── get_todays_games()          # Fetch schedule
│   ├── get_player_recent_stats()   # Player game logs
│   ├── get_team_defensive_stats()  # Team defense metrics
│   ├── calculate_rebound_trend()   # Trend analysis
│   ├── predict_player_performance() # Main prediction logic
│   └── analyze_todays_matchups()   # Generate all predictions
│
nba_app.py
├── Streamlit UI configuration
├── Sidebar controls
├── Prediction display
├── Analytics dashboard
└── Data export
```

## Performance

- **Initial load**: 10-30 seconds (fetches API data)
- **Subsequent updates**: 2-5 seconds (cached data)
- **Games analyzed**: All games for current day
- **Players analyzed**: Active players from today's teams

## Future Enhancements

Potential improvements:
- [ ] Machine learning prediction model
- [ ] Injury report integration
- [ ] Weather conditions for outdoor games
- [ ] Betting line comparison
- [ ] Historical accuracy tracking
- [ ] Player position-specific analysis
- [ ] Rest days and back-to-back game factors
- [ ] Home/away splits
- [ ] Pace of play adjustments
- [ ] Advanced metrics (PER, BPM, etc.)

## License

This project is for educational and entertainment purposes only.

## Disclaimer

**This tool is for research and entertainment purposes only.**
- Not intended as financial or betting advice
- Past performance doesn't guarantee future results
- Always do your own research
- NBA and team names are property of their respective owners

---

**Built with Claude Code**
Data provided by nba_api (unofficial NBA statistics API)
