# app/market_data.py
"""
Fetch OHLCV data from Yahoo Finance and normalise it.

Output columns: date, open, high, low, close, volume
"""

from typing import Literal

import pandas as pd
import yfinance as yf


def fetch_ohlcv(
    ticker: str,
    period: Literal["1mo", "3mo", "6mo", "1y", "2y"] = "6mo",
    interval: Literal["1d", "1h", "30m", "15m"] = "1d",
) -> pd.DataFrame:
    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )

    if df is None or df.empty:
        raise ValueError(
            f"No data returned for {ticker}. Try a longer period or a different interval."
        )

    # Collapse MultiIndex columns like ('Open', 'RELIANCE.NS') -> "Open"
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(c[0]) for c in df.columns]
    else:
        df.columns = [str(c) for c in df.columns]

    df = df.reset_index()

    # Normalise column names
    df.columns = [c.strip() for c in df.columns]

    rename_map = {
        "Date": "date",
        "Datetime": "date",
        "date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Adj_Close": "adj_close",
        "AdjClose": "adj_close",
        "Volume": "volume",
    }

    df = df.rename(columns=lambda c: rename_map.get(c, c))

    required = ["date", "open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        available = list(df.columns)
        raise ValueError(
            f"Downloaded data for {ticker} is missing required columns: {missing}. "
            f"Columns available: {available}"
        )

    out = df[required].copy()

    # Ensure numeric
    for col in ["open", "high", "low", "close", "volume"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out = out.dropna(subset=["date", "close"])

    if out.empty:
        raise ValueError(
            f"Downloaded data for {ticker} has no usable closing prices after cleaning."
        )

    return out.reset_index(drop=True)


def latest_snapshot_text(df: pd.DataFrame) -> str:
    """
    Convert the latest row into a short text snapshot for feeding into the LLM.
    """
    last = df.iloc[-1]
    return (
        f"Latest data for the instrument on {last['date'].date()}:\n"
        f"Open: {last['open']:.2f}, High: {last['high']:.2f}, "
        f"Low: {last['low']:.2f}, Close: {last['close']:.2f}, "
        f"Volume: {int(last['volume'])}"
    )
