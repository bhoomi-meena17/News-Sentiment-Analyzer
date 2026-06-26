import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="NewsPulse — Sentiment Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu_items={}


# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #F8F7F4;
    color: #1C1C1E;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E8E4DC;
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #1C1C1E;
}

/* Main container */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* Metric cards */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E8E4DC;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.metric-card .metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1C1C1E;
    line-height: 1;
}
.metric-card .metric-label {
    font-size: 0.78rem;
    font-weight: 500;
    color: #6B6B6B;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 0.4rem;
}
.metric-card .metric-delta {
    font-size: 0.82rem;
    font-weight: 500;
    margin-top: 0.3rem;
}

/* Article card */
.article-card {
    background: #FFFFFF;
    border: 1px solid #E8E4DC;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s;
}
.article-card:hover { box-shadow: 0 3px 10px rgba(0,0,0,0.08); }
.article-title {
    font-family: 'Playfair Display', serif;
    font-size: 0.97rem;
    font-weight: 600;
    color: #1C1C1E;
    margin-bottom: 0.3rem;
    line-height: 1.4;
}
.article-meta {
    font-size: 0.74rem;
    color: #8A8A8E;
    margin-bottom: 0.5rem;
}
.article-snippet {
    font-size: 0.83rem;
    color: #444;
    line-height: 1.55;
}

/* Sentiment badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.73rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-positive { background: #E6F4EA; color: #1E7A40; }
.badge-negative { background: #FDE8E8; color: #B91C1C; }
.badge-neutral  { background: #F0F0F0; color: #555;    }

/* Section header */
.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #1C1C1E;
    margin-bottom: 0.2rem;
}
.section-sub {
    font-size: 0.83rem;
    color: #8A8A8E;
    margin-bottom: 1.1rem;
}

/* Page header */
.page-header {
    border-bottom: 2px solid #E8E4DC;
    padding-bottom: 0.8rem;
    margin-bottom: 1.4rem;
}
.page-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #1C1C1E;
}
.page-tagline {
    font-size: 0.88rem;
    color: #6B6B6B;
    margin-top: 0.15rem;
}

/* Expander */
.streamlit-expanderHeader {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-size: 0.85rem;
    font-weight: 500;
}

/* Remove default streamlit top padding */
#MainMenu, header, footer { visibility: visible; }
            
/* Always show sidebar toggle */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    top: 0.5rem !important;
    left: 0.5rem !important;
    z-index: 999999 !important;
    background: #FFFFFF !important;
    border: 1px solid #E8E4DC !important;
    border-radius: 6px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
}

/* Divider */
hr { border-color: #E8E4DC; margin: 1.2rem 0; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #F8F7F4; }
::-webkit-scrollbar-thumb { background: #D0CBC0; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📰 NewsPulse")
    st.markdown("<p style='font-size:0.8rem;color:#8A8A8E;margin-top:-0.5rem;'>News Sentiment Intelligence</p>", unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🏠 Dashboard", "🔍 Search & Analyze", "📊 Topic Clustering", "💡 Insights & Export"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### ⚙️ Settings")

    category = st.selectbox("Category", [
        "technology", "business", "science", "health",
        "entertainment", "sports", "world"
    ])

    num_articles = st.slider("Articles to fetch", 20, 100, 40, step=10)

    st.markdown("---")
    fetch_btn = st.button("🔄 Refresh Feed", width="stretch", type="primary")

    st.markdown("""
    <div style='margin-top:2rem;padding:0.8rem;background:#F0EDE7;border-radius:8px;'>
    <p style='font-size:0.75rem;color:#6B6B6B;margin:0;line-height:1.6;'>
    <b>How it works:</b><br>
    Fetches RSS feeds → VADER + TextBlob sentiment → TF-IDF vectorisation → K-Means clustering → Trend analysis
    </p>
    </div>
    """, unsafe_allow_html=True)

# ── Page routing ──────────────────────────────────────────────────────────────
if page == "🏠 Dashboard":
    from views import dashboard
    dashboard.render(category, num_articles, fetch_btn)
elif page == "🔍 Search & Analyze":
    from views import search
    search.render()
elif page == "📊 Topic Clustering":
    from views import clustering
    clustering.render(category, num_articles, fetch_btn)
elif page == "💡 Insights & Export":
    from views import insights
    insights.render(category, num_articles, fetch_btn)
