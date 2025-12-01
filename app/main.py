# app/main.py
from typing import Literal

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fingpt_model import FinGPT  # uses OpenAI + Gemini (no Grok)
from market_data import fetch_ohlcv, latest_snapshot_text
from technicals import (
    add_technical_indicators,
    technical_snapshot_text,
    combine_market_and_technicals_text,
)
from ui_components import (
    inject_global_css,
    render_github_in_sidebar,
    render_app_title,
    render_section_header,
    render_footer,
)

# ----- Streamlit page config -----
st.set_page_config(
    page_title="FinGPT Trading Assistant",
    layout="wide",
)

# Global CSS / theme
inject_global_css()


def plot_candlestick(df: pd.DataFrame, ticker: str):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["date"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="OHLC",
            )
        ]
    )
    fig.update_layout(
        title=f"{ticker} - Candlestick",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height=500,
    )
    return fig


def main():
    # Top animated title tile
    render_app_title()

    # ----- Sidebar: Market & backend -----
    # GitHub icon inside the "Market Input" header in the sidebar
    render_github_in_sidebar("https://github.com/tharunprinz")  # ⬅️ put your GitHub URL here

    default_ticker = "RELIANCE.NS"
    ticker = st.sidebar.text_input("Ticker (Yahoo Finance symbol)", value=default_ticker)

    period: Literal["1mo", "3mo", "6mo", "1y", "2y"] = st.sidebar.selectbox(
        "History Period",
        options=["1mo", "3mo", "6mo", "1y", "2y"],
        index=2,
    )

    interval: Literal["1d", "1h", "30m", "15m"] = st.sidebar.selectbox(
        "Candle Interval",
        options=["1d", "1h", "30m", "15m"],
        index=0,
    )

    # LLM backend selector (label hidden – no "LLM backend" text)
    backend_choice = st.sidebar.radio(
        label="",
        options=[
            "OpenAI – GPT-4o-mini",
            "Gemini – 2.5-flash",
        ],
        index=0,
        label_visibility="collapsed",
    )

    if backend_choice.startswith("OpenAI"):
        backend: Literal["openai", "gemini"] = "openai"
        openai_model = "gpt-4o-mini"
        gemini_model = "gemini-2.5-flash"
    else:
        backend = "gemini"
        openai_model = "gpt-4o-mini"
        gemini_model = "gemini-2.5-flash"

    st.sidebar.markdown("---")
    st.sidebar.write("Load market data first, then run analysis on the right panel.")

    # Session state for data
    if "df" not in st.session_state:
        st.session_state.df = None
    if "df_tech" not in st.session_state:
        st.session_state.df_tech = None

    col_data, col_chat = st.columns([2, 1])

    # ===== LEFT: Market Data & Chart =====
    with col_data:
        render_section_header("📊", "Market Data & Candlesticks")

        if st.button("Load Market Data"):
            try:
                df = fetch_ohlcv(ticker=ticker, period=period, interval=interval)
                df_tech = add_technical_indicators(df)

                st.session_state.df = df
                st.session_state.df_tech = df_tech

                st.success(f"Loaded {len(df)} rows for {ticker}.")
            except Exception as e:
                # Clean error (no tracebacks, no file paths)
                st.error(f"Error loading data: {e}")

        if st.session_state.df is not None:
            df = st.session_state.df
            df_tech = st.session_state.df_tech

            st.plotly_chart(
                plot_candlestick(df, ticker),
                width="stretch",
            )

            with st.expander("Show raw data"):
                st.dataframe(df.tail(50))

            with st.expander("Show technical indicators (latest rows)"):
                st.dataframe(df_tech.tail(20))

    # ===== RIGHT: AI Analysis =====
    with col_chat:
        render_section_header("🤖", "AI Analysis & Suggestions")

        user_question = st.text_area(
            "Ask about this market (educational only, not financial advice):",
            value=(
                "What is the overall trend and momentum for this instrument? "
                "What are the key support and resistance zones, and what are the "
                "main risks to watch out for?"
            ),
            height=180,
        )

        if st.button("Run Analysis"):
            if st.session_state.df is None or st.session_state.df_tech is None:
                st.warning("Load market data first.")
            else:
                with st.spinner("Running analysis..."):
                    try:
                        raw_snap = latest_snapshot_text(st.session_state.df)
                        tech_snap = technical_snapshot_text(st.session_state.df_tech)
                        combined = combine_market_and_technicals_text(
                            raw_snapshot=raw_snap,
                            tech_snapshot=tech_snap,
                            ticker=ticker,
                        )

                        fingpt = FinGPT(
                            backend=backend,
                            openai_model=openai_model,
                            gemini_model=gemini_model,
                        )

                        analysis = fingpt.analyse(
                            market_snapshot=combined,
                            user_question=user_question,
                        )

                        st.markdown("### 📊 Analysis Result")
                        st.write(analysis)
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error running analysis: {e}")

    # Footer
    render_footer()


if __name__ == "__main__":
    main()
