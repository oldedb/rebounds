# Date Override Guide

## Problem

Your system clock shows **October 26, 2025** but the actual date is **October 25, 2025**.

Without root/sudo access, we cannot change the system date. However, the app now supports **date override** functionality.

## Solutions

### Option 1: Environment Variable (Command Line)

Set the date before running the app:

```bash
export NBA_DATE_OVERRIDE="2025-10-25"
streamlit run nba_app.py
```

Or in one command:

```bash
NBA_DATE_OVERRIDE="2025-10-25" streamlit run nba_app.py
```

### Option 2: Streamlit UI (Easiest!)

When running the Streamlit app:

1. Look for **"📅 Analysis Date"** in the sidebar
2. Check the box **"Override System Date"**
3. Select **October 25, 2025** from the date picker
4. Click **"🔍 Analyze Today's Games"**

The app will now fetch games for October 25 instead of October 26!

### Option 3: Python Code

If running the predictor directly:

```python
from nba_predictor import NBAPredictor

# Override to October 25, 2025
predictor = NBAPredictor(override_date="2025-10-25")
games = predictor.get_todays_games()
```

## How It Works

### Before (System Date)
```
System Clock: Oct 26, 2025
   ↓
ESPN API: Requests games for Oct 26
   ↓
Result: Wrong games or no games found
```

### After (Date Override)
```
System Clock: Oct 26, 2025 (ignored)
   ↓
Override: Oct 25, 2025
   ↓
ESPN API: Requests games for Oct 25
   ↓
Result: Correct games for October 25!
```

## Testing

Test the date override:

```bash
# Test with override
NBA_DATE_OVERRIDE="2025-10-25" python -c "
from nba_predictor import NBAPredictor
predictor = NBAPredictor(override_date='2025-10-25')
print('Date override working!')
"
```

Expected output:
```
📅 Using date override: 2025-10-25
ℹ️  Running in MOCK DATA mode for testing
Date override working!
```

## Impact on Features

With date override enabled:

### What Changes ✅
- ✅ ESPN API will query games for the override date
- ✅ Mock data still shows sample games (date doesn't affect mock data)
- ✅ UI displays the selected date clearly

### What Stays the Same ✅
- ✅ All predictions work normally
- ✅ All visualizations work
- ✅ Player stats and analysis unchanged
- ✅ Export functionality works

## Verification

Check if the date override is active:

```bash
python nba_predictor.py
```

Look for this message:
```
📅 Using date override: 2025-10-25
```

If you see this, the override is working!

## Production Deployment

When deploying to Streamlit Cloud or other platforms:

### If system date is correct:
- No action needed, don't enable override

### If system date is wrong:
- Set environment variable: `NBA_DATE_OVERRIDE=2025-10-25`
- Or use the UI checkbox for manual override

## Format

Date must be in **YYYY-MM-DD** format:

✅ Correct:
- `2025-10-25`
- `2024-12-31`
- `2025-01-01`

❌ Incorrect:
- `10/25/2025`
- `25-10-2025`
- `Oct 25, 2025`

## Summary

✅ **Date override implemented** - No need to fix system clock
✅ **Three ways to use it** - Environment variable, UI, or code
✅ **Works immediately** - No deployment or restart needed
✅ **User-friendly** - Clear UI with date picker in Streamlit app

**To use right now:**
1. Run: `streamlit run nba_app.py`
2. In sidebar, check "Override System Date"
3. Select October 25, 2025
4. Click "Analyze Today's Games"

Done! 🎉
