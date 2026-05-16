"""Digit-inspired professional theme: yellow, black, light gray."""

from contextlib import contextmanager
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent

# Digit Insurance palette
YELLOW = "#FFC107"
YELLOW_DARK = "#E6AC00"
BLACK = "#111111"
GRAY_DARK = "#4B5563"
GRAY_MID = "#9CA3AF"
GRAY_LIGHT = "#E5E7EB"
BG_PAGE = "#F8F9FA"
WHITE = "#FFFFFF"
SUCCESS = "#16A34A"
DANGER = "#DC2626"
CURRENCY_SYMBOL = "₹"


def format_inr(value: float, decimals: int = 0) -> str:
    """Format a number as Indian Rupees."""
    if decimals == 0:
        return f"{CURRENCY_SYMBOL}{value:,.0f}"
    return f"{CURRENCY_SYMBOL}{value:,.{decimals}f}"

CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {{
        --digit-yellow: {YELLOW};
        --digit-yellow-dark: {YELLOW_DARK};
        --digit-black: {BLACK};
        --digit-gray: {GRAY_DARK};
        --digit-bg: {BG_PAGE};
        --digit-white: {WHITE};
        --section-gap: 2rem;
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    .stApp {{
        background-color: var(--digit-bg) !important;
    }}

    /* Main content area */
    .main .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 1180px;
    }}

    /* Typography */
    h1 {{
        color: var(--digit-black) !important;
        font-weight: 800 !important;
        font-size: 2.25rem !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
        margin-bottom: 0.5rem !important;
    }}
    h2, h3 {{
        color: var(--digit-black) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
        margin-top: 0.25rem !important;
    }}
    h2 {{ font-size: 1.35rem !important; margin-bottom: 0.75rem !important; }}
    h3 {{ font-size: 1.1rem !important; }}
    p, li, .stMarkdown {{
        color: {GRAY_DARK} !important;
        line-height: 1.65 !important;
        font-size: 0.95rem !important;
    }}

    hr {{
        margin: 2rem 0 !important;
        border: none !important;
        border-top: 1px solid {GRAY_LIGHT} !important;
    }}

    /* Sidebar — clean white nav like Digit */
    [data-testid="stSidebar"] {{
        background: var(--digit-white) !important;
        border-right: 1px solid {GRAY_LIGHT} !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.5rem !important;
    }}
    [data-testid="stSidebar"] [data-testid="stMarkdown"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {{
        color: {GRAY_DARK} !important;
    }}
    [data-testid="stSidebar"] h1 {{
        color: var(--digit-black) !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
    }}

    /* Nav links */
    [data-testid="stSidebarNav"] ul {{
        padding-top: 0.5rem !important;
    }}
    [data-testid="stSidebarNav"] a {{
        border-radius: 999px !important;
        padding: 0.45rem 0.85rem !important;
        font-weight: 500 !important;
        color: {GRAY_DARK} !important;
    }}
    [data-testid="stSidebarNav"] a:hover {{
        background: #FFF8E1 !important;
        color: var(--digit-black) !important;
    }}
    [data-testid="stSidebarNav"] a[aria-current="page"] {{
        background: var(--digit-yellow) !important;
        color: var(--digit-black) !important;
        font-weight: 600 !important;
    }}

    /* Metrics */
    div[data-testid="stMetric"] {{
        background: var(--digit-white) !important;
        border: 1px solid {GRAY_LIGHT} !important;
        border-radius: 16px !important;
        padding: 1.25rem 1.5rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }}
    div[data-testid="stMetric"] label {{
        color: {GRAY_MID} !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: var(--digit-black) !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }}

    /* Primary buttons — pill yellow */
    .stButton > button[kind="primary"],
  .stButton > button[data-testid="stBaseButton-primary"] {{
        background: var(--digit-yellow) !important;
        color: var(--digit-black) !important;
        border: none !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.5rem !important;
        box-shadow: 0 2px 8px rgba(255, 193, 7, 0.45) !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: var(--digit-yellow-dark) !important;
    }}
    .stButton > button[kind="secondary"] {{
        border-radius: 999px !important;
        border: 1px solid {GRAY_LIGHT} !important;
        color: var(--digit-black) !important;
        background: white !important;
        font-weight: 500 !important;
    }}

    /* Expanders */
    .streamlit-expanderHeader {{
        background: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }}
    details {{
        border: 1px solid {GRAY_LIGHT} !important;
        border-radius: 16px !important;
        background: white !important;
        margin-bottom: 0.75rem !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    }}

    /* Dataframes & code in cards */
    [data-testid="stDataFrame"], [data-testid="stCode"] {{
        border-radius: 12px !important;
    }}

    /* Alerts */
    [data-testid="stAlert"] {{
        border-radius: 12px !important;
    }}
    div[data-baseweb="notification"] {{
        border-radius: 12px !important;
    }}

    /* Custom components */
    .hero-banner {{
        background: var(--digit-white);
        border-radius: 20px;
        padding: 2.5rem 2.75rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        border: 1px solid {GRAY_LIGHT};
    }}
    .hero-banner h1 {{
        margin: 0 0 0.35rem 0 !important;
        font-size: 2rem !important;
    }}
    .hero-sub {{
        color: {GRAY_DARK} !important;
        font-size: 1.05rem !important;
        margin: 0 0 1.25rem 0 !important;
        line-height: 1.5 !important;
    }}
    .hero-tag {{
        display: inline-block;
        background: var(--digit-yellow);
        color: var(--digit-black);
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        margin-bottom: 1rem;
        letter-spacing: 0.02em;
    }}

    .pro-section {{
        background: var(--digit-white);
        border-radius: 20px;
        padding: 1.75rem 2rem;
        margin-bottom: var(--section-gap);
        border: 1px solid {GRAY_LIGHT};
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }}
    .pro-section-title {{
        color: var(--digit-black) !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        margin: 0 0 1rem 0 !important;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--digit-yellow);
        display: inline-block;
        width: 100%;
    }}

    .insight-card {{
        background: #FFFBEB;
        border-left: 4px solid var(--digit-yellow);
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.25rem;
        margin: 1rem 0 1.5rem 0;
        color: {GRAY_DARK} !important;
        font-size: 0.9rem !important;
        line-height: 1.6 !important;
    }}

    .prediction-box {{
        background: var(--digit-yellow);
        color: var(--digit-black);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        text-align: center;
        font-size: 1.65rem;
        font-weight: 800;
        margin: 1.5rem 0;
        box-shadow: 0 6px 20px rgba(255, 193, 7, 0.4);
        border: 1px solid {YELLOW_DARK};
    }}
    .risk-low {{
        background: #ECFDF5;
        color: #065F46;
        border: 2px solid #10B981;
        padding: 1.5rem 2rem;
        border-radius: 20px;
        font-size: 1.15rem;
        font-weight: 600;
        margin: 1.25rem 0;
        text-align: center;
    }}
    .risk-high {{
        background: #FEF2F2;
        color: #991B1B;
        border: 2px solid #EF4444;
        padding: 1.5rem 2rem;
        border-radius: 20px;
        font-size: 1.15rem;
        font-weight: 600;
        margin: 1.25rem 0;
        text-align: center;
    }}

    .tech-pill-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }}
    .tech-pill {{
        background: #FFF8E1;
        color: var(--digit-black);
        border: 1px solid var(--digit-yellow);
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }}

    .page-spacer {{ height: 0.5rem; }}
    .chart-block {{ margin-bottom: 1.5rem; }}

    /* Bordered containers (content sections) */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--digit-white) !important;
        border-radius: 20px !important;
        border: 1px solid {GRAY_LIGHT} !important;
        padding: 0.5rem 0.25rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04) !important;
    }}
</style>
"""


def apply_theme():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", tag: str = ""):
    """Digit-style hero block at top of each page."""
    tag_html = f'<span class="hero-tag">{tag}</span>' if tag else ""
    sub_html = f'<p class="hero-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="hero-banner">
            {tag_html}
            <h1>{title}</h1>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def content_section(title: str):
    with st.container(border=True):
        st.markdown(
            f'<p class="pro-section-title">{title}</p>',
            unsafe_allow_html=True,
        )
        yield

def insight(text: str):
    st.markdown(f'<div class="insight-card">{text}</div>', unsafe_allow_html=True)


def tech_pills(items: list[str]):
    pills = "".join(f'<span class="tech-pill">{x}</span>' for x in items)
    st.markdown(f'<div class="tech-pill-row">{pills}</div>', unsafe_allow_html=True)


def spacer(size: str = "md"):
    heights = {"sm": "0.75rem", "md": "1.25rem", "lg": "2rem"}
    st.markdown(f'<div style="height:{heights.get(size, "1.25rem")}"></div>', unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("### Insurance Analytics")
        st.caption("Claim Risk & Customer Analysis")
        st.markdown("---")
        if st.button("Rebuild ML models", use_container_width=True, type="primary"):
            import shutil

            models_dir = APP_DIR / "models"
            if models_dir.exists():
                shutil.rmtree(models_dir)
                models_dir.mkdir()
            st.cache_resource.clear()
            st.cache_data.clear()
            st.success("Models will retrain on next ML page visit.")
