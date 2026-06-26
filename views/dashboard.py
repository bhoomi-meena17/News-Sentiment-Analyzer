"""
pages/dashboard.py  —  Main overview dashboard
"""

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data import fetch_articles, get_sentiment_summary
from utils import charts


def _badge(label: str) -> str:
    cls = f"badge badge-{label}"
    return f'<span class="{cls}">{label.upper()}</span>'


def render(category: str, num_articles: int, refresh: bool):
    # Header
    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>📰 Live News Dashboard</div>
        <div class='page-tagline'>Real-time sentiment intelligence across today's headlines</div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch
    if refresh:
        st.cache_data.clear()

    with st.spinner("Fetching and analysing articles…"):
        df = fetch_articles(category, num_articles)

    if df.empty:
        st.warning("⚠️ Could not fetch articles right now. Check your internet connection or try another category.")
        return

    # Demo mode detection
    try:
        from utils.mock_data import MOCK_ARTICLES
        is_demo = not df.empty and df["title"].iloc[0] in [a[0] for a in MOCK_ARTICLES.get(category, [])]
        if is_demo:
            st.info("📋 **Demo Mode** — Showing curated sample data. On deployment with internet access, live RSS feeds are fetched automatically.")
    except Exception:
        pass

    summary = get_sentiment_summary(df)

    # ── KPI row ───────────────────────────────────────────────────────────────
    st.markdown("### Overview")
    k1, k2, k3, k4, k5 = st.columns(5)

    def kpi(col, val, label, delta="", delta_color="#1E7A40"):
        col.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{val}</div>
            <div class='metric-label'>{label}</div>
            {'<div class="metric-delta" style="color:' + delta_color + ';">' + delta + '</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)

    kpi(k1, summary["total"], "Articles Analysed")
    pct_pos = f"{summary['positive']/summary['total']*100:.0f}% positive"
    kpi(k2, summary["positive"], "Positive", pct_pos, "#1E7A40")
    pct_neg = f"{summary['negative']/summary['total']*100:.0f}% negative"
    kpi(k3, summary["negative"], "Negative", pct_neg, "#B91C1C")
    kpi(k4, summary["neutral"], "Neutral")
    mood_color = "#1E7A40" if summary["avg_compound"] > 0 else "#B91C1C" if summary["avg_compound"] < 0 else "#555"
    kpi(k5, f"{summary['avg_compound']:+.3f}", "Avg Sentiment", "", mood_color)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row ────────────────────────────────────────────────────────────
    c1, c2 = st.columns([1, 1.6])
    with c1:
        st.markdown("<div class='section-header'>Sentiment Mix</div>", unsafe_allow_html=True)
        st.plotly_chart(charts.sentiment_donut(df), width="stretch", config={"displayModeBar": False})
    with c2:
        st.markdown("<div class='section-header'>Score Distribution</div>", unsafe_allow_html=True)
        st.plotly_chart(charts.compound_histogram(df), width="stretch", config={"displayModeBar": False})

    st.markdown("---")

    # ── Timeline ─────────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Publication Timeline</div>", unsafe_allow_html=True)
    st.plotly_chart(charts.timeline_bar(df), width="stretch", config={"displayModeBar": False})

    st.markdown("---")

    # ── Sentiment by source ───────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Sentiment by Source</div>"
                "<div class='section-sub'>Average compound score per outlet</div>", unsafe_allow_html=True)
    st.plotly_chart(charts.sentiment_by_source(df), width="stretch", config={"displayModeBar": False})

    st.markdown("---")

    # ── Article feed ─────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Latest Headlines</div>", unsafe_allow_html=True)

    filter_col, sort_col = st.columns([2, 1])
    with filter_col:
        sent_filter = st.multiselect(
            "Filter by sentiment",
            ["positive", "neutral", "negative"],
            default=["positive", "neutral", "negative"],
            label_visibility="collapsed"
        )
    with sort_col:
        sort_by = st.selectbox("Sort by", ["Date (newest)", "Most Positive", "Most Negative"],
                               label_visibility="collapsed")

    filtered = df[df["label"].isin(sent_filter)].copy()
    if sort_by == "Most Positive":
        filtered = filtered.sort_values("compound", ascending=False)
    elif sort_by == "Most Negative":
        filtered = filtered.sort_values("compound")

    st.markdown(f"<div class='section-sub'>{len(filtered)} articles shown</div>", unsafe_allow_html=True)

    for _, row in filtered.head(20).iterrows():
        url_html = f'<a href="{row["url"]}" target="_blank" style="text-decoration:none;color:inherit;">' \
                   if row.get("url") else ""
        close_a = "</a>" if row.get("url") else ""
        st.markdown(f"""
        <div class='article-card'>
            <div class='article-title'>{url_html}{row['title']}{close_a}</div>
            <div class='article-meta'>
                📡 {row.get('source','?')} &nbsp;·&nbsp; 🕐 {row.get('published','?')} &nbsp;·&nbsp;
                {_badge(row['label'])} &nbsp;
                <span style='font-size:0.74rem;color:#6B6B6B;'>score: {row['compound']:+.3f}</span>
            </div>
            {'<div class="article-snippet">' + row["summary"] + '</div>' if row.get("summary") else ''}
        </div>
        """, unsafe_allow_html=True)

    # Save to session for other pages
    st.session_state["df"] = df
    st.session_state["category"] = category
