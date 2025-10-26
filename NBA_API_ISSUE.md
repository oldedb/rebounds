# NBA API Access Issue

## Problem

The NBA Stats API (`stats.nba.com`) is currently **blocking all programmatic access** with 403 errors, even when using the official `nba_api` Python library. This affects the ability to fetch today's game schedule and player statistics.

### Error Details
```
HTTP 403 - Access denied
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

### What We've Tried
- ✗ Using `nba_api` library's built-in `scoreboardv2` endpoint
- ✗ Direct HTTP requests with browser-like headers
- ✗ Multiple header configurations (Firefox, Chrome user agents)
- ✗ Testing with historical dates (confirmed API block, not data availability issue)

## Why This Happened

The NBA has tightened restrictions on their Stats API in recent months to prevent unauthorized scraping and ensure data integrity. They now require:
1. More sophisticated authentication
2. Potentially rotating API keys
3. Rate limiting compliance
4. Verified origin/referrer validation

## Solutions

### Option 1: Use Alternative Data Sources (Recommended)

**ESPN API (Free, Unofficial)**
```python
# Example: Get today's NBA scores from ESPN
import requests

url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
response = requests.get(url)
data = response.json()
games = data.get('events', [])
```

**Other Options:**
- **balldontlie.io** - Free NBA stats API
- **SportsData.io** - Commercial API with free tier
- **The Odds API** - Includes game schedules and odds
- **RapidAPI NBA endpoints** - Various providers

### Option 2: Use NBA API Proxy Services

Some community members have created proxy services that handle NBA API authentication:
- `nba-api-proxy` - GitHub projects that wrap the NBA API
- Cloudflare Workers-based proxies

### Option 3: Web Scraping (Last Resort)

Scrape from NBA.com or ESPN.com directly:
```python
from bs4 import BeautifulSoup
import requests

# Scrape from NBA.com schedule page
url = "https://www.nba.com/games"
response = requests.get(url)
# Parse HTML for game data
```

**Caution:** Web scraping may violate terms of service and is fragile.

### Option 4: Paid API Access

- **Sportradar NBA API** - Official NBA data partner ($$$)
- **Stats Perform** - Professional sports data ($$$$)

## Recommended Next Steps

### 1. Migrate to ESPN API (Quick Fix)

I can update the code to use ESPN's free API, which provides:
- ✓ Today's games schedule
- ✓ Team rosters and stats
- ✓ Player statistics
- ✓ Live scores
- ✓ No authentication required

**Pros:**
- Free and reliable
- No authentication
- Good documentation
- Active community

**Cons:**
- Less detailed than NBA Stats API
- Some advanced metrics may be missing
- Unofficial API (could change)

### 2. Add Support for Multiple Data Sources

Create an adapter pattern that supports multiple backends:
```python
# config.py
DATA_SOURCE = "espn"  # or "balldontlie", "sportsdata", etc.

# Then switch between providers based on config
```

### 3. Cache Data Locally

For development/testing, create sample data files:
```python
# Use cached game data when API is unavailable
if not games:
    games = load_cached_games()
```

## Impact on Current Features

**What Still Works:**
- ✓ App UI and navigation
- ✓ Data visualization (with sample data)
- ✓ Prediction algorithms
- ✓ Analytics calculations

**What's Broken:**
- ✗ Fetching today's live game schedule
- ✗ Real-time player statistics
- ✗ Current season data
- ✗ Live game updates

## Testing

Current date tested: `2025-10-26`
- NBA API scoreboardv2: **BLOCKED (403)**
- Historical date (2024-02-14): **BLOCKED (403)**
- Both nba_api library and direct HTTP: **BLOCKED**

## Recommendation

**I recommend switching to ESPN's API immediately** to restore functionality. This will allow the app to work again while we evaluate long-term solutions.

Would you like me to:
1. **Update the code to use ESPN API** (restores functionality today)
2. **Add multi-source support** (more robust, takes longer)
3. **Create mock data for testing** (temporary fix)

Let me know which approach you prefer!
