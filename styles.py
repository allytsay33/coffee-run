"""CSS overrides that make the Streamlit demo feel mobile-first."""

import streamlit as st


def inject_mobile_styles():
    """Constrain the app to a phone-like canvas and style shared controls."""
    st.markdown(
        """
        <style>
        :root {
            --coffee: #a56335;
            --coffee-dark: #7f4827;
            --paper: #fffdf9;
            --soft: #f6f1ec;
            --line: #eadfd6;
            --muted: #7b746f;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background: #eeeeee;
        }

        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            max-width: 430px;
            min-height: 100vh;
            padding: 1.15rem 1rem 6rem;
            background: var(--paper);
            box-shadow: 0 18px 48px rgba(55, 37, 26, 0.12);
        }

        h1 {
            color: var(--coffee-dark);
            text-align: center;
            font-size: 1.35rem !important;
            line-height: 1.2 !important;
            margin: 0.25rem 0 0.9rem !important;
        }

        h2, h3 {
            color: var(--coffee-dark);
            letter-spacing: 0;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
        [data-testid="stTextArea"] textarea {
            border-radius: 16px;
            background: #f5f2ef;
            border-color: transparent;
        }

        [data-testid="stButton"] button,
        [data-testid="stFormSubmitButton"] button,
        [data-testid="stLinkButton"] a {
            border-radius: 999px;
            border-color: var(--line);
        }

        [data-testid="stButton"] button[kind="primary"],
        [data-testid="stFormSubmitButton"] button[kind="primary"] {
            background: var(--coffee);
            border-color: var(--coffee);
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 18px;
            border-color: rgba(165, 99, 53, 0.15);
            box-shadow: 0 8px 24px rgba(73, 45, 28, 0.07);
        }

        .coffee-screen-title {
            color: var(--coffee-dark);
            text-align: center;
            font-size: 1.35rem;
            font-weight: 760;
            margin: 0.15rem 0 0.9rem;
        }

        .coffee-section-title {
            color: var(--coffee-dark);
            font-size: 1.22rem;
            font-weight: 760;
            margin: 1.1rem 0 0.45rem;
        }

        .coffee-muted {
            color: var(--muted);
            font-size: 0.82rem;
        }

        .coffee-card-title {
            color: var(--coffee);
            font-size: 1.02rem;
            font-weight: 760;
            margin-bottom: 0.1rem;
        }

        .bottom-nav {
            position: fixed;
            left: 50%;
            bottom: 16px;
            transform: translateX(-50%);
            width: min(360px, calc(100vw - 48px));
            z-index: 1000;
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(165, 99, 53, 0.12);
            border-radius: 999px;
            box-shadow: 0 12px 32px rgba(60, 41, 30, 0.18);
            padding: 0.28rem;
        }

        .bottom-nav [data-testid="stRadio"] > label {
            display: none;
        }

        .bottom-nav [role="radiogroup"] {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.18rem;
        }

        .bottom-nav [role="radio"] {
            justify-content: center;
            border-radius: 999px;
            padding: 0.45rem 0.25rem;
            min-height: 44px;
        }

        .bottom-nav [role="radio"][aria-checked="true"] {
            background: #eaded5;
            color: var(--coffee-dark);
        }

        .bottom-nav p {
            font-size: 0.78rem;
            font-weight: 650;
        }

        .stImage img {
            border-radius: 14px;
        }

        @media (max-width: 520px) {
            .block-container {
                max-width: 100vw;
                box-shadow: none;
                padding-left: 0.9rem;
                padding-right: 0.9rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
