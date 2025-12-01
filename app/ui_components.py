# app/ui_components.py
"""
Small helpers for styling and layout of the Streamlit app.
Only OpenAI + Gemini are supported (no Grok).
"""

import streamlit as st


def inject_global_css() -> None:
    st.markdown(
        """
        <style>
        /* ===== Global App Look ===== */
        .stApp {
            background: radial-gradient(circle at top left, #0f172a, #020617);
            color: #e5e7eb;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        /* Center content a bit more */
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            max-width: 1200px;
        }

        /* ===== Title Card ===== */
        .app-title-card {
            background: radial-gradient(circle at top left, rgba(56,189,248,0.12), rgba(15,23,42,0.95));
            border-radius: 20px;
            padding: 18px 22px;
            box-shadow: 0 20px 60px rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.4);
            backdrop-filter: blur(16px);
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.6s ease-out;
        }

        .app-title-card::before {
            content: "";
            position: absolute;
            inset: -40%;
            background: conic-gradient(
                from 180deg,
                transparent 0deg,
                rgba(56,189,248,0.25),
                rgba(168,85,247,0.2),
                rgba(249,115,22,0.25),
                transparent 300deg
            );
            opacity: 0.4;
            filter: blur(22px);
            animation: spinGlow 18s linear infinite;
        }

        .app-title-inner {
            position: relative;
            z-index: 1;
        }

        .app-title {
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            background: linear-gradient(120deg, #38bdf8, #a855f7, #f97316);
            -webkit-background-clip: text;
            color: transparent;
        }

        .app-subtitle {
            color: #9ca3af;
            font-size: 0.95rem;
            margin-top: 4px;
        }

        /* ===== Section Headings (“tiles”) ===== */
        .section-header {
            margin-bottom: 0.9rem;
            padding: 10px 14px;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,64,175,0.95));
            border: 1px solid rgba(96, 165, 250, 0.45);
            box-shadow: 0 14px 35px rgba(15, 23, 42, 0.8);
            display: flex;
            align-items: center;
            gap: 10px;
            animation: fadeInUp 0.7s ease-out;
        }

        .section-header-icon {
            font-size: 1.4rem;
        }

        .section-header-text {
            font-weight: 700;
            font-size: 1.0rem;
        }

        /* ===== Sidebar “Market Input” + GitHub Badge ===== */
        .sidebar-header-with-github {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            margin-bottom: 0.4rem;
            margin-top: 0.4rem;
        }

        .sidebar-header-with-github-title {
            font-weight: 700;
            font-size: 1.02rem;
        }

        .sidebar-github-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            background: rgba(15, 23, 42, 0.98);
            padding: 8px;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.9);
            transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        }

        .sidebar-github-icon img {
            width: 34px;
            height: 34px;
        }

        .sidebar-github-icon:hover {
            transform: translateY(-2px) scale(1.05);
            background: rgba(15, 23, 42, 1);
            box-shadow: 0 20px 45px rgba(15, 23, 42, 1);
        }

        /* ===== Buttons / Inputs Animations ===== */
        .stButton button {
            border-radius: 999px;
            padding: 0.4rem 1.2rem;
            border: 1px solid rgba(148,163,184,0.5);
            background: linear-gradient(135deg, #1d4ed8, #7c3aed);
            color: #e5e7eb;
            font-weight: 600;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.8);
            transition: transform 0.12s ease-out, box-shadow 0.12s ease-out, background 0.15s ease-out;
        }
        .stButton button:hover {
            transform: translateY(-1px) scale(1.02);
            box-shadow: 0 18px 40px rgba(15, 23, 42, 1);
            background: linear-gradient(135deg, #2563eb, #8b5cf6);
        }

        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea > div > textarea {
            border-radius: 12px !important;
        }

        /* ===== Footer ===== */
        .app-footer {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(148, 163, 184, 0.35);
            text-align: center;
            font-size: 0.85rem;
            color: #9ca3af;
        }

        /* ===== Keyframe Animations ===== */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes spinGlow {
            from { transform: rotate(0deg); }
            to   { transform: rotate(360deg); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_github_in_sidebar(profile_url: str) -> None:
    """
    GitHub icon next to 'Market Input' heading in the sidebar.
    """
    st.sidebar.markdown(
        f"""
        <div class="sidebar-header-with-github">
            <div class="sidebar-header-with-github-title">Market Input</div>
            <a class="sidebar-github-icon" href="{profile_url}" target="_blank" rel="noopener noreferrer">
                <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub" />
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_app_title() -> None:
    """
    Main title tile at the top (single animated tile).
    """
    st.markdown(
        """
        <div class="app-title-card">
          <div class="app-title-inner">
            <div class="app-title">FinGPT Trading Assistant</div>
            <div class="app-subtitle">
              AI-powered market snapshot and technical analysis.<br/>
              <span style="opacity:0.9;">Educational only — not financial advice.</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(icon: str, text: str) -> None:
    """
    Small animated tile used above each main section.
    (No extra blank card - this is exactly the header you see.)
    """
    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-header-icon">{icon}</div>
            <div class="section-header-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        '<div class="app-footer">Powered by Geminai and OpenAi</div>',
        unsafe_allow_html=True,
    )
