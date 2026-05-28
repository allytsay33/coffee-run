"""CSS overrides that make the Streamlit demo feel mobile-first."""

import streamlit as st


def inject_mobile_styles():
    """Constrain the app to a phone-like canvas and style shared controls."""
    st.markdown(
        """
        <style>
        @import url("https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:FILL@0..1&display=swap");

        :root {
            --coffee: #7c5e43;
            --coffee-dark: #2d241e;
            --paper: #faf9f6;
            --surface: #ffffff;
            --soft: #f3f1e9;
            --line: #e6e2d3;
            --muted: #a8a18c;
            --gold: #c78b35;
            --streamlit-toolbar-height: 4.65rem;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background: var(--paper);
            color: var(--coffee-dark);
        }

        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            max-width: 460px;
            min-height: 100vh;
            padding: var(--streamlit-toolbar-height) 1rem 6.4rem;
            background: var(--paper);
            box-shadow: 0 0 0 1px rgba(230, 226, 211, 0.72), 0 18px 48px rgba(55, 37, 26, 0.08);
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
            background: var(--soft);
            border-color: transparent;
            color: var(--coffee-dark);
            font-size: 0.84rem;
        }

        [data-testid="stButton"] button,
        [data-testid="stFormSubmitButton"] button,
        [data-testid="stLinkButton"] a {
            border-radius: 999px;
            border-color: var(--line);
            color: var(--coffee);
            font-size: 0.78rem;
            font-weight: 650;
            background: var(--surface);
        }

        [data-testid="stButton"] button[kind="primary"],
        [data-testid="stFormSubmitButton"] button[kind="primary"] {
            background: var(--coffee);
            border-color: var(--coffee);
            color: var(--paper);
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 24px;
            border-color: var(--line);
            background: var(--surface);
            box-shadow: 0 5px 18px rgba(73, 45, 28, 0.045);
        }

        .coffee-screen-title {
            color: var(--coffee-dark);
            text-align: center;
            font-family: Georgia, serif;
            font-size: 1.25rem;
            font-weight: 760;
            margin: 0.15rem 0 0.9rem;
        }

        .coffee-section-title {
            color: var(--coffee-dark);
            font-family: Georgia, serif;
            font-size: 1.13rem;
            font-weight: 760;
            margin: 1.1rem 0 0.45rem;
        }

        .coffee-muted {
            color: var(--muted);
            font-size: 0.82rem;
        }

        .coffee-card-title {
            color: var(--coffee-dark);
            font-family: Georgia, serif;
            font-size: 0.96rem;
            font-weight: 760;
            margin-bottom: 0.1rem;
        }

        .st-key-brewbound_header {
            position: sticky;
            top: 0;
            z-index: 900;
            margin: calc(-1 * var(--streamlit-toolbar-height)) -1rem 1rem;
            padding: 0.68rem 0.85rem 0.62rem;
            background: rgba(255, 255, 255, 0.94);
            border-bottom: 1px solid var(--line);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
        }

        .st-key-brewbound_header [data-testid="stHorizontalBlock"] {
            align-items: center;
            gap: 0.35rem;
        }

        .st-key-brewbound_header [data-testid="stColumn"] {
            display: flex !important;
            align-items: center !important;
        }

        .st-key-brewbound_header [data-testid="stVerticalBlock"] {
            gap: 0 !important;
            width: 100%;
            display: flex !important;
            align-items: center !important;
        }

        .st-key-brewbound_header [data-testid="stMarkdown"] {
            display: flex !important;
            align-items: center !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .st-key-brewbound_header [data-testid="stMarkdown"] p {
            margin: 0 !important;
            line-height: 1 !important;
        }

        .brand-lockup {
            display: flex;
            align-items: center;
            gap: 0.52rem;
        }

        .brand-mark {
            height: 2.12rem;
            width: 2.12rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 0.68rem;
            color: var(--paper);
            background: var(--coffee);
            font-family: Georgia, serif;
            font-size: 1.14rem;
            font-weight: 700;
        }

        .brand-copy {
            display: flex;
            flex-direction: column;
            line-height: 1.05;
        }

        .brand-copy strong {
            color: var(--coffee-dark);
            font-family: Georgia, serif;
            font-size: 0.93rem;
            white-space: nowrap;
        }

        .brand-copy em {
            color: var(--coffee);
            font-style: italic;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .brand-copy small {
            color: var(--muted);
            font-size: 0.54rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            margin-top: 0.22rem;
        }

        .st-key-brewbound_header [data-testid="stButton"] button {
            height: 2.1rem;
            background: var(--coffee);
            border-color: var(--coffee);
            color: #fff;
            font-size: 1.02rem;
        }

        .st-key-header_brand_logo {
            margin-top: -5rem;
            height: 5rem;
            position: relative;
            z-index: 2;
        }

        .st-key-header_brand_logo button {
            height: 5rem !important;
            width: 150% !important;
            background: transparent !important;
            border-color: transparent !important;
            box-shadow: none !important;
            color: transparent !important;
            font-size: 0 !important;
            cursor: pointer !important;
        }

        .st-key-header_new_post button {
            width: 168px !important;
            min-width: 168px !important;
            margin-left: auto;
        }

        .st-key-header_profile_link button {
            min-height: 2.1rem;
            justify-content: flex-end;
            gap: 0.5rem;
            border-color: transparent !important;
            background: transparent !important;
            color: var(--coffee) !important;
            box-shadow: none !important;
            padding: 0 !important;
            font-size: 0.73rem !important;
            font-weight: 700 !important;
            white-space: nowrap;
        }


        .header-avatar {
            height: 2.1rem;
            width: 2.1rem;
            border: 1px solid var(--coffee);
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--soft);
            color: var(--coffee);
            font-weight: 700;
            margin-left: auto;
        }

        .header-user {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 0.65rem;
            color: var(--coffee);
            font-size: 0.73rem;
            font-weight: 700;
            white-space: nowrap;
        }

        .header-search-display {
            min-height: 2.4rem;
            border-radius: 999px;
            background: var(--soft);
            color: var(--muted);
            display: flex;
            align-items: center;
            padding: 0 1rem;
            font-size: 0.8rem;
            white-space: nowrap;
        }

        .view-heading {
            margin: 0.35rem 0 1rem;
        }

        .view-heading h2 {
            color: var(--coffee-dark);
            font-family: Georgia, serif;
            font-size: 1.45rem;
            font-weight: 700;
            line-height: 1.15;
            margin: 0 0 0.3rem;
        }

        .view-heading p {
            color: #746d65;
            font-size: 0.76rem;
            line-height: 1.55;
            margin: 0;
        }

        .toolbar-label {
            color: var(--coffee);
            font-size: 0.64rem;
            font-weight: 760;
            letter-spacing: 0.12em;
            margin: 0.78rem 0 0.36rem;
        }

        [data-testid="stPills"] button {
            background: #fff;
            border: 1px solid var(--line);
            color: var(--coffee);
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 650;
        }

        [data-testid="stPills"] button[aria-selected="true"] {
            background: var(--coffee);
            border-color: var(--coffee);
            color: var(--paper);
        }

        .st-key-brewbound_map {
            margin: 0.75rem -1rem 0.95rem;
            overflow: hidden;
            border-top: 1px solid var(--line);
            border-bottom: 1px solid var(--line);
        }

        .st-key-brewbound_map img {
            border-radius: 0 !important;
            display: block;
        }

        .map-status {
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            gap: 0.52rem;
            margin-bottom: -3.4rem;
            margin-left: 0.9rem;
            margin-right: 0.9rem;
            padding: 0.92rem 1rem;
            color: #07674e;
            background: rgba(233, 255, 247, 0.94);
            border: 1px solid #a2ead5;
            border-radius: 1rem;
            font-size: 0.8rem;
            font-weight: 650;
        }

        .map-status span {
            height: 0.55rem;
            width: 0.55rem;
            border-radius: 50%;
            background: #04bc84;
        }

        .map-status strong {
            margin-left: auto;
            padding: 0.16rem 0.42rem;
            background: #fff2c5;
            border-radius: 0.34rem;
            color: var(--coffee);
            font-size: 0.68rem;
        }

        .result-heading {
            color: var(--muted);
            font-size: 0.74rem;
            font-weight: 600;
            padding: 0.2rem 0 0.7rem;
        }

        .result-heading strong {
            color: var(--coffee-dark);
        }

        .cafe-result-head {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.55rem;
        }

        .rating-pill {
            display: inline-flex;
            align-items: center;
            flex-shrink: 0;
            border-radius: 999px;
            background: #fff8eb;
            color: var(--gold);
            padding: 0.15rem 0.42rem;
            font-size: 0.68rem;
            font-weight: 750;
        }

        .cafe-meta {
            color: #756f69;
            font-size: 0.66rem;
            margin: 0.2rem 0 0.58rem;
        }

        .tag-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.28rem;
            margin: 0.52rem 0 0.64rem;
        }

        .tag-row span {
            border-radius: 0.25rem;
            background: var(--soft);
            color: var(--coffee);
            padding: 0.16rem 0.36rem;
            font-size: 0.62rem;
            font-weight: 700;
        }

        .post-location {
            color: var(--coffee);
            font-size: 0.65rem;
            font-weight: 720;
            letter-spacing: 0.04em;
            margin-bottom: 0.34rem;
        }

        .post-author {
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--coffee);
            font-size: 0.72rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
        }

        .post-detail-header {
            display: flex;
            align-items: center;
            gap: 0.3rem;
            margin-bottom: 0.75rem;
        }

        .post-detail-info {
            display: flex;
            flex-direction: column;
            gap: 0.1rem;
        }

        .post-detail-info .post-location {
            margin-bottom: 0;
        }

        .post-detail-avatar {
            flex-shrink: 0;
            width: 48px;
            height: 48px;
            border-radius: 999px;
            background: var(--soft);
            color: var(--coffee);
            border: 1.5px solid var(--line);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.2rem;
        }

        .post-author-detail {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--coffee-dark);
            font-size: 1.05rem;
            font-weight: 700;
        }

        .st-key-post_detail_card .post-location {
            font-size: 0.9rem !important;
        }

        .st-key-post_detail_card .post-author {
            font-size: 1.15rem !important;
        }

        .st-key-post_detail_card .rating-pill {
            font-size: 0.95rem !important;
            padding: 0.2rem 0.6rem !important;
        }

        .st-key-post_detail_card .stImage {
            display: flex !important;
            justify-content: center !important;
        }

        .st-key-post_detail_card .stImage img {
            max-width: 500px !important;
            width: 100% !important;
            height: auto !important;
        }

        .post-preview-small {
            max-width: 500px;
            margin: 0 auto;
        }

        .post-preview {
            position: relative;
            border-radius: 14px;
            overflow: hidden;
            aspect-ratio: 4 / 3;
            margin-bottom: 0.65rem;
        }

        .post-preview img {
            height: 100%;
            width: 100%;
            display: block;
            object-fit: cover;
        }

        .post-preview span {
            position: absolute;
            left: 0.7rem;
            right: 0.7rem;
            bottom: 0.58rem;
            color: #fff;
            font-size: 0.63rem;
            font-weight: 750;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.55);
        }

        .post-copy {
            color: var(--coffee-dark);
            font-size: 0.79rem;
            line-height: 1.65;
            margin: 0 0 0.5rem;
        }

        .st-key-profile_identity [data-testid="stVerticalBlockBorderWrapper"] {
            padding-top: 0.2rem;
            text-align: center;
        }

        .profile-name {
            color: var(--coffee-dark);
            font-family: Georgia, serif;
            font-size: 1.2rem;
            font-weight: 720;
            text-align: center;
            margin-bottom: 0.12rem;
        }

        .profile-handle {
            color: var(--coffee);
            font-size: 0.72rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.45rem;
        }

        .profile-bio {
            color: #677084;
            line-height: 1.7;
            font-size: 0.8rem;
            max-width: 32rem;
        }

        .profile-section-title {
            color: #9c4509;
            font-size: 0.85rem;
            font-weight: 760;
            letter-spacing: 0.1em;
            margin-bottom: 1rem;
        }

        .top-cafe {
            min-height: 4.8rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            border: 1px solid var(--line);
            border-radius: 1.25rem;
            background: #fffdfa;
            padding: 0.8rem 1rem;
            flex-wrap: wrap;
        }

        .top-cafe b {
            height: 2.1rem;
            width: 2.1rem;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            color: #fff;
            background: var(--coffee);
            border-radius: 50%;
        }

        .top-cafe strong {
            color: #1e293b;
            font-size: 0.82rem;
        }

        .top-cafe small {
            color: var(--muted);
            margin-left: 2.82rem;
            margin-top: -1.18rem;
        }

        .top-cafe-empty b {
            color: var(--muted);
        }

        .top-cafe-empty span {
            color: var(--muted);
            font-size: 0.78rem;
            display: block;
            margin-top: 0.15rem;
        }

        /* ── Login back button ── */
        .st-key-login_back button,
        .st-key-register_back button {
            background: transparent !important;
            border-color: transparent !important;
            color: var(--coffee) !important;
            box-shadow: none !important;
            padding-left: 0 !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            justify-content: flex-start !important;
        }


        /* ── Profile TOP 3 container ── */

        .st-key-profile_top3 [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-profile_top3 [data-testid="stVerticalBlock"],
        .st-key-profile_top3 > div,
        .st-key-profile_top3 > div > div {
            padding-bottom: 0.8rem !important;
        }

        .st-key-profile_top3 [data-testid="stHorizontalBlock"] {
            margin-bottom: 0.3rem !important;
        }

        /* ── Login page ── */
        .login-logo {
            text-align: center;
            margin: 3rem auto 1.5rem;
        }

        .login-logo img {
            width: 110px;
            height: 110px;
            object-fit: cover;
            border-radius: 50%;
            border: 3px solid var(--line);
            box-shadow: 0 4px 18px rgba(124, 94, 67, 0.18);
        }

        .login-title {
            font-size: 2rem;
            font-weight: 700;
            color: var(--coffee-dark);
            text-align: center;
            letter-spacing: -0.02em;
            margin-bottom: 0.25rem;
        }

        .login-subtitle {
            font-size: 0.95rem;
            color: var(--muted);
            text-align: center;
            margin-bottom: 2.2rem;
        }

        .st-key-profile_subnav {
            margin: 1.1rem 0 1.25rem;
            border-bottom: 1px solid var(--line);
            padding-bottom: 0.35rem;
        }

        .st-key-profile_subnav [data-testid="stSegmentedControl"] {
            background: transparent;
        }

        .st-key-profile_tab_content {
            min-height: 22rem;
        }

        .st-key-profile_tab_content .coffee-section-title {
            margin-top: 1.2rem;
        }

        .st-key-liquid_glass_nav {
            position: fixed;
            left: 50%;
            bottom: max(16px, env(safe-area-inset-bottom));
            transform: translateX(-50%);
            width: min(360px, calc(100vw - 44px));
            z-index: 1000;
            background: rgba(255, 255, 255, 0.58);
            border: 1px solid rgba(255, 255, 255, 0.76);
            border-radius: 999px;
            box-shadow:
                0 14px 32px rgba(63, 51, 44, 0.12),
                inset 0 1px 0 rgba(255, 255, 255, 0.96),
                inset 0 -1px 0 rgba(255, 255, 255, 0.34);
            backdrop-filter: blur(22px) saturate(1.45);
            -webkit-backdrop-filter: blur(22px) saturate(1.45);
            padding: 0.34rem 0.4rem;
        }

        .st-key-liquid_glass_nav [data-testid="stRadio"] > label {
            display: none;
        }

        .st-key-liquid_glass_nav [role="radiogroup"] {
            display: flex;
            width: 100%;
            gap: 0;
            position: relative;
            isolation: isolate;
        }

        .st-key-liquid_glass_nav [role="radiogroup"]::before {
            content: "";
            position: absolute;
            z-index: -1;
            top: 0;
            bottom: 0;
            left: 0;
            width: calc(100% / 3);
            border-radius: 999px;
            background: rgba(225, 222, 219, 0.66);
            border: 1px solid rgba(255, 255, 255, 0.72);
            box-shadow:
                inset 0 1px 1px rgba(255, 255, 255, 0.84),
                0 5px 16px rgba(66, 50, 38, 0.08);
            transition: transform 260ms cubic-bezier(0.2, 0.82, 0.25, 1);
        }

        .st-key-liquid_glass_nav [role="radiogroup"]:has([data-baseweb="radio"]:nth-child(2) input:checked)::before {
            transform: translateX(100%);
        }

        .st-key-liquid_glass_nav [role="radiogroup"]:has([data-baseweb="radio"]:nth-child(3) input:checked)::before {
            transform: translateX(200%);
        }

        .st-key-liquid_glass_nav [data-baseweb="radio"] {
            display: flex;
            flex: 1 1 0;
            width: calc(100% / 3);
            min-width: 0;
            flex-direction: column;
            gap: 0.1rem;
            justify-content: center;
            align-items: center;
            border-radius: 999px;
            padding: 0.46rem 0.25rem 0.43rem;
            min-height: 64px;
            color: #393938;
            cursor: pointer;
            transition: color 180ms ease;
            text-align: center;
        }

        .st-key-liquid_glass_nav [data-baseweb="radio"] > div:first-child {
            display: none;
        }

        .st-key-liquid_glass_nav [data-baseweb="radio"]::before {
            display: block;
            font-family: "Material Symbols Rounded";
            font-size: 2rem;
            font-weight: normal;
            line-height: 1;
            font-variation-settings: "FILL" 1, "wght" 500, "GRAD" 0, "opsz" 32;
        }

        .st-key-liquid_glass_nav [data-baseweb="radio"]:nth-child(1)::before {
            content: "map";
        }

        .st-key-liquid_glass_nav [data-baseweb="radio"]:nth-child(2)::before {
            content: "forum";
        }

        .st-key-liquid_glass_nav [data-baseweb="radio"]:nth-child(3)::before {
            content: "account_circle";
        }

        .st-key-liquid_glass_nav [data-baseweb="radio"]:has(input:checked) {
            color: var(--coffee);
        }

        .st-key-liquid_glass_nav [data-baseweb="radio"] p {
            color: inherit;
            font-size: 0.9rem;
            font-weight: 670;
            line-height: 1.1;
            letter-spacing: 0;
        }

        .stImage img {
            border-radius: 14px;
        }

        .profile-avatar {
            width: 72px;
            height: 72px;
            margin: 0 auto 0.55rem;
            border-radius: 999px;
            background: var(--soft);
            color: var(--coffee);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
        }

        .gallery-placeholder {
            aspect-ratio: 1 / 1.18;
            background: #eee9e5;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #9c8f86;
            margin-bottom: 0.4rem;
        }

        @media (min-width: 769px) {
            .block-container {
                max-width: 1440px;
                padding: var(--streamlit-toolbar-height) 2.2rem 2.3rem 10.3rem;
                box-shadow: none;
            }

            .st-key-brewbound_header {
                width: min(calc(100vw - 4.4rem), 1600px) !important;
                max-width: min(calc(100vw - 4.4rem), 1600px) !important;
                min-width: min(calc(100vw - 4.4rem), 1600px) !important;
                margin: 0 0 1.3rem calc(-10.3rem + 2.2rem);
                padding: 0.82rem 3.8rem;
            }

            .brand-mark {
                height: 3.35rem;
                width: 3.35rem;
                border-radius: 1rem;
                font-size: 1.55rem;
            }

            .brand-copy strong {
                font-size: 1.55rem;
            }

            .brand-copy em {
                font-size: 1.25rem;
            }

            .brand-copy small {
                font-size: 0.64rem;
            }

            .header-search-display {
                height: 3.05rem;
                font-size: 0.94rem;
            }

            .st-key-brewbound_header [data-testid="stButton"] button {
                height: 3.05rem;
                font-size: 0.9rem;
            }

            .st-key-header_profile_link button {
                height: 3.05rem;
                font-size: 0.88rem !important;
            }

            .header-avatar {
                height: 3.05rem;
                width: 3.05rem;
            }

            .header-user {
                font-size: 0.88rem;
            }

            .st-key-liquid_glass_nav {
                position: fixed;
                left: max(1rem, calc((100vw - 1440px) / 2 + 1.1rem));
                top: calc(var(--streamlit-toolbar-height) + 6.25rem);
                bottom: auto;
                transform: none;
                width: 6.6rem;
                margin: 0;
                padding: 0.34rem;
                box-shadow: 0 12px 28px rgba(72, 55, 40, 0.08);
                border-color: var(--line);
                border-radius: 1.25rem;
                background: rgba(255, 253, 250, 0.86);
            }

            .st-key-liquid_glass_nav [role="radiogroup"] {
                flex-direction: column;
                gap: 0.16rem;
                align-items: center;
            }

            .st-key-liquid_glass_nav [role="radiogroup"]::before {
                display: none;
            }

            .st-key-liquid_glass_nav [data-baseweb="radio"] {
                flex: 0 0 auto;
                width: 5.55rem;
                min-height: 2.95rem;
                flex-direction: column;
                gap: 0.08rem;
                padding: 0.32rem 0.22rem;
            }

            .st-key-liquid_glass_nav [data-baseweb="radio"]::before {
                font-size: 1.35rem;
            }

            .st-key-liquid_glass_nav [data-baseweb="radio"]:has(input:checked) {
                background: rgba(225, 222, 219, 0.66);
                border: 1px solid rgba(255, 255, 255, 0.72);
                box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.84);
            }

            .explore-title {
                display: none;
            }

            .st-key-brewbound_map {
                margin: 0 -0.1rem 1.5rem;
                border: 1px solid var(--line);
                border-radius: 0;
            }

            .st-key-brewbound_map img {
                max-height: 40rem;
                object-fit: cover;
                width: 100%;
            }

            .st-key-explore_results_panel {
                max-height: calc(100vh - 14.5rem);
                overflow-y: auto;
                padding-right: 0.45rem;
            }

            .st-key-explore_focus_panel {
                position: sticky;
                top: 1rem;
                min-height: 34rem;
            }

            .st-key-cafe_detail_panel {
                background: var(--surface);
                border: 1px solid var(--line);
                border-radius: 1.2rem;
                padding: 1rem 1.1rem 1.2rem;
                max-height: calc(100vh - 14.5rem);
                overflow-y: auto;
            }

            .map-status {
                margin: 1rem 1rem -4.45rem;
                padding: 1.15rem 1rem;
                font-size: 0.96rem;
            }

            .toolbar-label {
                font-size: 0.82rem;
                margin-top: 0.7rem;
            }

            [data-testid="stPills"] button {
                font-size: 0.82rem;
                padding: 0.42rem 0.92rem;
            }

            .result-heading {
                border-top: 1px solid var(--line);
                margin-top: 0;
                padding: 1rem 0 0.9rem;
                font-size: 0.88rem;
            }

            .coffee-card-title {
                font-size: 1.2rem;
            }

            .cafe-meta {
                font-size: 0.82rem;
            }

            .post-copy {
                font-size: 0.83rem;
            }

            .view-heading h2 {
                font-size: 1.7rem;
            }

            .st-key-profile_identity,
            .st-key-profile_top3,
            .st-key-profile_map {
                margin-bottom: 1.55rem;
            }

            .st-key-profile_identity [data-testid="stVerticalBlockBorderWrapper"],
            .st-key-profile_top3 [data-testid="stVerticalBlockBorderWrapper"],
            .st-key-profile_map [data-testid="stVerticalBlockBorderWrapper"] {
                padding: 1.6rem 1.8rem;
            }

            .profile-avatar {
                height: 8.2rem;
                width: 8.2rem;
                font-size: 2.5rem;
            }

            .profile-name {
                font-size: 1.65rem;
                text-align: left;
            }

            .profile-handle {
                font-size: 0.9rem;
                text-align: left;
            }

            .profile-bio {
                font-size: 0.78rem;
                line-height: 1.55;
                margin-bottom: 0;
            }

            .st-key-profile_subnav {
                margin-top: 0.85rem;
            }

            .st-key-profile_subnav [data-testid="stSegmentedControl"] {
                max-width: 30rem;
            }

            .st-key-profile_map .st-key-brewbound_map {
                margin: 0.7rem 0 0;
                border-radius: 0.65rem;
                overflow: hidden;
            }
        }

        @media (max-width: 768px) {
            .block-container {
                max-width: 100vw;
                box-shadow: none;
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
