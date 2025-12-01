# app/technicals.py
"""
Compute a few simple technical indicators and turn them into text.
"""

from typing import Tuple

import numpy as np
import pandas as pd


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def _macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add basic technical indicators to a copy of the OHLCV DataFrame.
    Ensures all inputs are 1-D Series.
    """
    out = df.copy()

    close = pd.Series(out["close"].to_numpy().reshape(-1), index=out.index)

    # Moving averages
    out["sma_20"] = close.rolling(window=20, min_periods=5).mean()
    out["sma_50"] = close.rolling(window=50, min_periods=10).mean()
    out["ema_20"] = close.ewm(span=20, adjust=False).mean()

    # RSI
    out["rsi_14"] = _rsi(close, period=14)

    # MACD
    macd_line, signal_line, hist = _macd(close, fast=12, slow=26, signal=9)
    out["macd"] = macd_line
    out["macd_signal"] = signal_line
    out["macd_hist"] = hist

    # Simple volatility
    out["returns"] = close.pct_change()
    out["volatility_20"] = out["returns"].rolling(window=20, min_periods=5).std()

    return out


def technical_snapshot_text(df_tech: pd.DataFrame) -> str:
    """
    Turn the latest technical indicators into a concise text summary.
    """
    row = df_tech.iloc[-1]
    parts = []

    if not np.isnan(row.get("sma_20", np.nan)):
        parts.append(f"SMA20={row['sma_20']:.2f}")
    if not np.isnan(row.get("sma_50", np.nan)):
        parts.append(f"SMA50={row['sma_50']:.2f}")
    if not np.isnan(row.get("ema_20", np.nan)):
        parts.append(f"EMA20={row['ema_20']:.2f}")

    if not np.isnan(row.get("rsi_14", np.nan)):
        parts.append(f"RSI14={row['rsi_14']:.1f}")

    if not np.isnan(row.get("macd", np.nan)):
        parts.append(
            f"MACD={row['macd']:.4f}, "
            f"Signal={row['macd_signal']:.4f}, "
            f"Hist={row['macd_hist']:.4f}"
        )

    if not np.isnan(row.get("volatility_20", np.nan)):
        parts.append(f"20-day volatility={row['volatility_20']:.4f}")

    return " | ".join(parts)


def combine_market_and_technicals_text(
    raw_snapshot: str,
    tech_snapshot: str,
    ticker: str,
) -> str:
    """
    Combine raw OHLCV snapshot and technicals into a single prompt for the LLM.
    """
    return (
        f"Instrument: {ticker}\n\n"
        f"Market snapshot:\n{raw_snapshot}\n\n"
        f"Technical indicators (latest):\n{tech_snapshot}\n\n"
        f"Use this data to provide trading analysis, including trend, "
        f"momentum, key levels, and risk factors."
    )
