# app/fingpt_model.py
"""
FinGPT wrapper that can talk to:
  - OpenAI Chat Completions (GPT models)
  - Google Gemini (text-only)

API keys are read from:
  1. streamlit.secrets["OPENAI_API_KEY"] / ["GEMINI_API_KEY"]
  2. Environment variables OPENAI_API_KEY / GEMINI_API_KEY

No keys are hard-coded in this file.
"""

from typing import Literal, Optional
import os

from openai import OpenAI, APIConnectionError  # type: ignore
import google.generativeai as genai  # type: ignore

try:
    import streamlit as st  # type: ignore
except Exception:  # running outside Streamlit
    st = None  # type: ignore


BackendType = Literal["openai", "gemini"]


def _get_secret(name: str) -> str:
    """Try Streamlit secrets, then environment variables."""
    val: Optional[str] = None

    # 1) Streamlit secrets
    if st is not None:
        try:
            if name in st.secrets:
                val = str(st.secrets[name])
        except Exception:
            pass

    # 2) Environment variable
    if not val:
        val = os.getenv(name)

    if not val:
        raise RuntimeError(
            f"{name} is not set. In deployment, add it to Streamlit secrets or "
            f"export it as an environment variable."
        )

    return val


class FinGPT:
    def __init__(
        self,
        backend: BackendType,
        openai_model: str = "gpt-4o-mini",
        gemini_model: str = "gemini-2.5-flash",
    ):
        self.backend: BackendType = backend
        self.openai_model = openai_model
        self.gemini_model = gemini_model

        if backend == "openai":
            openai_key = _get_secret("OPENAI_API_KEY")
            self._client = OpenAI(api_key=openai_key)
            self._gemini_model = None
        else:
            gemini_key = _get_secret("GEMINI_API_KEY")
            genai.configure(api_key=gemini_key)
            # IMPORTANT: use bare model id, not "models/..."
            self._gemini_model = genai.GenerativeModel(self.gemini_model)
            self._client = None

    def analyse(
        self,
        market_snapshot: str,
        user_question: str,
        max_new_tokens: int = 800,
    ) -> str:
        """Run LLM analysis for the given market snapshot + user question."""
        if self.backend == "openai":
            return self._analyse_openai(market_snapshot, user_question, max_new_tokens)
        else:
            return self._analyse_gemini(market_snapshot, user_question, max_new_tokens)

    # ----- OpenAI -----
    def _analyse_openai(
        self,
        market_snapshot: str,
        user_question: str,
        max_new_tokens: int,
    ) -> str:
        if self._client is None:
            raise RuntimeError("OpenAI client is not initialised.")

        system_message = (
            "You are FinGPT, a trading assistant. "
            "You analyse OHLCV price action and technical indicators. "
            "Always include:\n"
            "- Overall trend and momentum\n"
            "- Key support and resistance zones\n"
            "- Important risks to watch\n"
            "This is strictly educational, NOT financial advice."
        )

        user_content = (
            "Here is recent market and technical data for one instrument.\n\n"
            f"{market_snapshot}\n\n"
            "User question:\n"
            f"{user_question}"
        )

        try:
            resp = self._client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.7,
                max_tokens=max_new_tokens,
            )
        except APIConnectionError:
            raise RuntimeError(
                "Connection error while contacting OpenAI. "
                "Check your internet connection and that this machine can reach api.openai.com."
            )
        except Exception as e:  # generic
            raise RuntimeError(f"OpenAI request failed: {e}")

        msg = resp.choices[0].message.content or ""
        return msg.strip()

    # ----- Gemini -----
    def _analyse_gemini(
        self,
        market_snapshot: str,
        user_question: str,
        max_new_tokens: int,
    ) -> str:
        if self._gemini_model is None:
            raise RuntimeError("Gemini model is not initialised.")

        system_message = (
            "You are FinGPT, a trading assistant. "
            "You analyse OHLCV price action and technical indicators. "
            "Always include:\n"
            "- Overall trend and momentum\n"
            "- Key support and resistance zones\n"
            "- Important risks to watch\n"
            "This is strictly educational, NOT financial advice."
        )

        prompt = (
            system_message
            + "\n\nHere is recent market and technical data for one instrument:\n"
            + market_snapshot
            + "\n\nUser question:\n"
            + user_question
        )

        try:
            resp = self._gemini_model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": max_new_tokens,
                },
            )
        except Exception as e:  # network, invalid model id, etc.
            raise RuntimeError(f"Gemini request failed: {e}")

        # Avoid using resp.text (which can throw if safety blocked)
        candidates = getattr(resp, "candidates", None)
        if not candidates:
            raise RuntimeError(
                "Gemini response was empty. This can happen if the request "
                "was blocked by safety filters."
            )

        cand = candidates[0]
        finish_reason = getattr(cand, "finish_reason", None)
        # SAFETY blocks often show as finish_reason = 'SAFETY'
        if finish_reason and str(finish_reason).upper().endswith("SAFETY"):
            raise RuntimeError(
                "Gemini blocked this request due to safety filters. "
                "Make your question more general and educational, and avoid "
                "asking for exact 'what should I buy/sell/hold' signals."
            )

        parts = getattr(cand, "content", None)
        text_out = ""
        if parts and getattr(parts, "parts", None):
            for p in parts.parts:
                text_out += getattr(p, "text", "") or ""

        if not text_out.strip():
            raise RuntimeError(
                "Gemini did not return any text. This may be due to safety filters."
            )

        return text_out.strip()
