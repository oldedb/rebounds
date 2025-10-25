#!/usr/bin/env python3
"""
NBA Rebound Prediction App

Streamlit web interface for analyzing NBA player rebounding predictions
based on recent trends and opposing team defensive strength.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from nba_predictor import NBAPredictor, PlayerPrediction

# Page configuration
st.set_page_config(
    page_title="NBA Rebound Predictor",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .prediction-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #0066cc;
    }
    .over-prediction {
        border-left-color: #28a745;
        background-color: #e8f5e9;
    }
    .under-prediction {
        border-left-color: #dc3545;
        background-color: #ffebee;
    }
    .neutral-prediction {
        border-left-color: #ffc107;
        background-color: #fff8e1;
    }
    .high-confidence {
        font-weight: bold;
        font-size: 1.2rem;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏀 NBA Rebound Predictor</div>', unsafe_allow_html=True)
st.markdown("**Predict player rebounding performance based on recent trends and defensive matchups**")
st.markdown("---")

# Sidebar configuration
st.sidebar.header("⚙️ Settings")

recent_games = st.sidebar.slider(
    "Recent Games to Analyze",
    min_value=3,
    max_value=10,
    value=5,
    step=1,
    help="Number of recent games to analyze for trend calculation"
)

min_season_avg = st.sidebar.slider(
    "Minimum Season Rebound Average",
    min_value=1.0,
    max_value=8.0,
    value=3.0,
    step=0.5,
    help="Filter out players below this rebound average"
)

show_neutral = st.sidebar.checkbox(
    "Show Neutral Predictions",
    value=False,
    help="Include players with neutral prediction (no strong signal)"
)

st.sidebar.markdown("---")

# Initialize predictor
@st.cache_resource(hash_funcs={int: lambda x: x})
def get_predictor(num_games, _cache_version=2):  # Increment version to bust cache
    return NBAPredictor(recent_games=num_games)

predictor = get_predictor(recent_games, _cache_version=2)

# Main content
st.sidebar.markdown("### 📅 Analysis Date")
st.sidebar.info(f"**{datetime.now().strftime('%B %d, %Y')}**")

analyze_button = st.sidebar.button("🔍 Analyze Today's Games", type="primary", use_container_width=True)

if analyze_button or 'predictions' not in st.session_state:
    with st.spinner("Fetching today's NBA games..."):
        games = predictor.get_todays_games()

    if not games:
        st.warning("⚠️ No NBA games scheduled for today. Try again on a game day!")
        st.session_state['predictions'] = []
        st.session_state['games'] = []
    else:
        st.success(f"✅ Found {len(games)} games today")

        with st.spinner(f"Analyzing matchups and generating predictions..."):
            predictions = predictor.analyze_todays_matchups()

            # Filter predictions
            filtered_predictions = [
                p for p in predictions
                if p.season_avg_reb >= min_season_avg
            ]

            if not show_neutral:
                filtered_predictions = [
                    p for p in filtered_predictions
                    if p.prediction != "NEUTRAL"
                ]

        st.session_state['predictions'] = filtered_predictions
        st.session_state['games'] = games

# Display results
if 'predictions' in st.session_state and st.session_state['predictions']:
    predictions = st.session_state['predictions']

    # Summary metrics
    st.header("📊 Prediction Summary")

    col1, col2, col3, col4 = st.columns(4)

    over_count = sum(1 for p in predictions if p.prediction == "OVER")
    under_count = sum(1 for p in predictions if p.prediction == "UNDER")
    neutral_count = sum(1 for p in predictions if p.prediction == "NEUTRAL")
    high_conf = sum(1 for p in predictions if p.confidence == "HIGH")

    with col1:
        st.metric("Total Predictions", len(predictions))

    with col2:
        st.metric("OVER Predictions", over_count, delta="Strong matchups")

    with col3:
        st.metric("UNDER Predictions", under_count, delta="Tough matchups")

    with col4:
        st.metric("High Confidence", high_conf)

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🎯 Predictions", "📈 Analytics", "ℹ️ About"])

    with tab1:
        st.subheader("Player Predictions")

        # Filter controls
        col1, col2 = st.columns(2)

        with col1:
            filter_pred = st.selectbox(
                "Filter by Prediction",
                ["All", "OVER", "UNDER", "NEUTRAL"],
                index=0
            )

        with col2:
            filter_conf = st.selectbox(
                "Filter by Confidence",
                ["All", "HIGH", "MEDIUM", "LOW"],
                index=0
            )

        # Apply filters
        filtered = predictions
        if filter_pred != "All":
            filtered = [p for p in filtered if p.prediction == filter_pred]
        if filter_conf != "All":
            filtered = [p for p in filtered if p.confidence == filter_conf]

        # Sort by confidence (HIGH first)
        confidence_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        filtered.sort(key=lambda x: confidence_order[x.confidence])

        # Display predictions
        if not filtered:
            st.info("No predictions match the selected filters")
        else:
            for pred in filtered:
                # Determine card class
                if pred.prediction == "OVER":
                    card_class = "prediction-card over-prediction"
                    icon = "📈"
                elif pred.prediction == "UNDER":
                    card_class = "prediction-card under-prediction"
                    icon = "📉"
                else:
                    card_class = "prediction-card neutral-prediction"
                    icon = "➡️"

                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)

                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    conf_class = "high-confidence" if pred.confidence == "HIGH" else ""
                    st.markdown(f'<p class="{conf_class}">{icon} {pred.player_name}</p>', unsafe_allow_html=True)
                    st.markdown(f"**{pred.team} vs {pred.opponent}**")

                with col2:
                    st.metric("Season Avg", f"{pred.season_avg_reb:.1f}")
                    st.metric("Recent Avg", f"{pred.recent_avg_reb:.1f}",
                             delta=f"{pred.recent_avg_reb - pred.season_avg_reb:+.1f}")

                with col3:
                    st.metric("Prediction", pred.prediction)
                    st.metric("Confidence", pred.confidence)

                # Reasoning
                with st.expander("📋 Analysis Details"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Player Metrics**")
                        st.markdown(f"- Trend: {pred.recent_trend.upper()}")
                        st.markdown(f"- Season Avg: {pred.season_avg_reb:.1f} reb/game")
                        st.markdown(f"- Recent Avg: {pred.recent_avg_reb:.1f} reb/game")

                    with col2:
                        st.markdown("**Opponent Metrics**")
                        st.markdown(f"- Defense Rating: {pred.opp_def_rating:.1f}")
                        st.markdown(f"- Rebounds Allowed: {pred.opp_reb_allowed:.1f}/game")
                        st.markdown(f"- Pace: {pred.opp_pace:.1f} poss/48min")
                        st.markdown(f"- FG% Allowed: {pred.opp_fg_pct:.1f}%")
                        st.markdown(f"- Shot Volume: {pred.opp_fga_per_game:.1f} FGA/game")

                    st.markdown("**Reasoning:**")
                    for reason in pred.reasoning:
                        st.markdown(f"- {reason}")

                st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("Analytics Dashboard")

        if predictions:
            # Create DataFrame
            df = pd.DataFrame({
                'Player': [p.player_name for p in predictions],
                'Team': [p.team for p in predictions],
                'Opponent': [p.opponent for p in predictions],
                'Season Avg': [p.season_avg_reb for p in predictions],
                'Recent Avg': [p.recent_avg_reb for p in predictions],
                'Difference': [p.recent_avg_reb - p.season_avg_reb for p in predictions],
                'Trend': [p.recent_trend for p in predictions],
                'Prediction': [p.prediction for p in predictions],
                'Confidence': [p.confidence for p in predictions],
                'Opp Def Rating': [p.opp_def_rating for p in predictions],
                'Opp Reb Allowed': [p.opp_reb_allowed for p in predictions],
                'Opp Pace': [p.opp_pace for p in predictions],
                'Opp FG%': [p.opp_fg_pct for p in predictions],
                'Opp FGA/Game': [p.opp_fga_per_game for p in predictions]
            })

            # Prediction distribution
            col1, col2 = st.columns(2)

            with col1:
                # Pie chart - Prediction distribution
                pred_counts = df['Prediction'].value_counts()
                colors = {'OVER': '#28a745', 'UNDER': '#dc3545', 'NEUTRAL': '#ffc107'}
                fig = go.Figure(data=[go.Pie(
                    labels=pred_counts.index,
                    values=pred_counts.values,
                    marker_colors=[colors.get(x, '#999') for x in pred_counts.index],
                    hole=0.3
                )])
                fig.update_layout(title="Prediction Distribution", height=400)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Confidence distribution
                conf_counts = df['Confidence'].value_counts()
                fig = px.bar(
                    x=conf_counts.index,
                    y=conf_counts.values,
                    labels={'x': 'Confidence', 'y': 'Count'},
                    title='Confidence Distribution',
                    color=conf_counts.index,
                    color_discrete_map={'HIGH': '#28a745', 'MEDIUM': '#ffc107', 'LOW': '#dc3545'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            # Scatter plot - Recent vs Season Average
            fig = px.scatter(
                df,
                x='Season Avg',
                y='Recent Avg',
                color='Prediction',
                size='Opp Reb Allowed',
                hover_data=['Player', 'Team', 'Opponent', 'Confidence'],
                title='Recent vs Season Average Rebounds',
                color_discrete_map={'OVER': '#28a745', 'UNDER': '#dc3545', 'NEUTRAL': '#ffc107'}
            )

            # Add diagonal line (y=x)
            max_val = max(df['Season Avg'].max(), df['Recent Avg'].max())
            fig.add_trace(go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode='lines',
                name='Equal Line',
                line=dict(dash='dash', color='gray')
            ))

            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

            # Data table
            st.subheader("Complete Data Table")
            st.dataframe(
                df.style.background_gradient(subset=['Recent Avg'], cmap='RdYlGn')
                  .format({
                      'Season Avg': '{:.1f}',
                      'Recent Avg': '{:.1f}',
                      'Difference': '{:+.1f}',
                      'Opp Def Rating': '{:.1f}',
                      'Opp Reb Allowed': '{:.1f}',
                      'Opp Pace': '{:.1f}',
                      'Opp FG%': '{:.1f}',
                      'Opp FGA/Game': '{:.1f}'
                  }),
                use_container_width=True
            )

            # Download CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Predictions CSV",
                data=csv,
                file_name=f"nba_rebound_predictions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    with tab3:
        st.subheader("About This Tool")

        st.markdown("""
        ## How It Works

        This NBA Rebound Predictor analyzes today's matchups and predicts whether players will
        **over-perform** or **under-perform** their season rebounding averages based on:

        ### Analysis Factors

        1. **Recent Form**
           - Compares recent games (default: last 5) to season average
           - Identifies hot/cold streaks

        2. **Rebounding Trends**
           - Calculates trajectory (increasing, decreasing, or stable)
           - Uses linear regression on recent game data

        3. **Opponent Defense**
           - Defensive rating (lower = better defense)
           - Rebounds allowed per game

        4. **Pace & Tempo**
           - Possessions per 48 minutes
           - Higher pace = more shot opportunities = more rebounds available

        5. **Shooting Efficiency**
           - Opponent field goal percentage allowed
           - Lower FG% = more missed shots = more rebounding opportunities

        6. **Shot Volume**
           - Field goal attempts per game
           - More shots = more rebound opportunities

        7. **Combined Matchup Analysis**
           - Integrates all factors to generate prediction
           - Assigns confidence level (HIGH/MEDIUM/LOW)

        ### Prediction Types

        - **OVER** 📈: Player likely to exceed season average
        - **UNDER** 📉: Player likely to fall below season average
        - **NEUTRAL** ➡️: No strong signal either way

        ### Confidence Levels

        - **HIGH**: Multiple strong factors align
        - **MEDIUM**: Some positive factors
        - **LOW**: Mixed or weak signals

        ### Best Practices

        - Focus on **HIGH confidence** predictions
        - Consider **OVER** predictions for favorable matchups
        - Look for players with **increasing trends**
        - Factor in opponent's defensive weaknesses

        ### Data Source

        This tool uses the unofficial NBA API to fetch:
        - Live game schedules
        - Player statistics
        - Team defensive metrics
        - Historical game data

        ### Limitations

        - Predictions are for entertainment/research purposes only
        - Does not account for injuries, rest, or lineup changes
        - Historical performance doesn't guarantee future results
        - Requires active NBA season for live data

        ---

        **Built with Claude Code** | Data from NBA API
        """)

elif 'predictions' in st.session_state and not st.session_state['predictions']:
    st.info("👈 Click 'Analyze Today's Games' in the sidebar to generate predictions")

    st.markdown("""
    ## Welcome to NBA Rebound Predictor!

    This tool helps you identify strong rebounding matchups by analyzing:
    - Player recent performance trends
    - Season averages
    - Opposing team defensive strength
    - Historical rebounding patterns

    ### Quick Start

    1. Click **"Analyze Today's Games"** in the sidebar
    2. Review predictions with confidence ratings
    3. Filter by OVER/UNDER predictions
    4. Export data for further analysis

    **Note:** This tool requires active NBA games to generate predictions.
    """)
else:
    st.info("👈 Click 'Analyze Today's Games' in the sidebar to get started!")
