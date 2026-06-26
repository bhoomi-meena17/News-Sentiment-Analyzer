"""
pages/insights.py  —  Derived insights, subjectivity deep-dive, export
"""

import streamlit as st
import pandas as pd
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data import fetch_articles, get_sentiment_summary
from utils import charts


def render(category: str, num_articles: int, refresh: bool):
    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>💡 Insights & Export</div>
        <div class='page-tagline'>Deeper analysis, actionable observations, and data export</div>
    </div>
    """, unsafe_allow_html=True)

    if refresh:
        st.cache_data.clear()

    # Use cached df from session if available
    df = st.session_state.get("df", None)
    if df is None or df.empty:
        with st.spinner("Loading articles…"):
            df = fetch_articles(category, num_articles)
        if df.empty:
            st.warning("No data. Refresh the feed from the sidebar.")
            return
        st.session_state["df"] = df

    summary = get_sentiment_summary(df)

    # ── Insight cards ─────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Key Observations</div>", unsafe_allow_html=True)

    mood = "optimistic" if summary["avg_compound"] > 0.05 else \
           "pessimistic" if summary["avg_compound"] < -0.05 else "mixed/neutral"
    dominant = max(["positive", "negative", "neutral"],
                   key=lambda l: summary.get(l, 0))

    insights = [
        ("🌡️ Overall Mood", f"Today's {category} news leans <b>{mood}</b> with an average sentiment of <b>{summary['avg_compound']:+.3f}</b>.", ""),
        ("📊 Dominant Tone", f"<b>{dominant.capitalize()}</b> coverage makes up {summary[dominant]/summary['total']*100:.0f}% of all articles.", ""),
        ("⭐ Most Positive", f'<span style="font-style:italic;">"{summary["most_positive"][:120]}…"</span>', "#E6F4EA"),
        ("⚠️ Most Negative", f'<span style="font-style:italic;">"{summary["most_negative"][:120]}…"</span>', "#FDE8E8"),
        ("📝 Subjectivity", f"Average subjectivity score: <b>{summary['avg_subjectivity']:.3f}</b> — {'fairly subjective reporting' if summary['avg_subjectivity']>0.5 else 'mostly factual reporting'}.", ""),
    ]

    for title, body, bg in insights:
        bg_style = f"background:{bg};" if bg else "background:#FFFFFF;"
        st.markdown(f"""
        <div style='{bg_style}border:1px solid #E8E4DC;border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:0.6rem;'>
            <div style='font-weight:600;font-size:0.9rem;margin-bottom:0.25rem;'>{title}</div>
            <div style='font-size:0.84rem;color:#444;line-height:1.55;'>{body}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Subjectivity vs Sentiment quadrant ────────────────────────────────────
    st.markdown("<div class='section-header'>Sentiment × Subjectivity Quadrant</div>"
                "<div class='section-sub'>Understand how objective or opinionated the reporting is</div>",
                unsafe_allow_html=True)

    st.plotly_chart(charts.subjectivity_scatter(df), width="stretch",
                    config={"displayModeBar": False})

    st.markdown("""
    <div style='display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-top:0.3rem;'>
        <div style='background:#E6F4EA;border-radius:8px;padding:0.6rem;font-size:0.78rem;color:#1E7A40;'>
            <b>Top-right (Positive + Subjective):</b> Enthusiastic, opinion-heavy positive coverage
        </div>
        <div style='background:#FDE8E8;border-radius:8px;padding:0.6rem;font-size:0.78rem;color:#B91C1C;'>
            <b>Top-left (Negative + Subjective):</b> Alarmist or editorial negative commentary
        </div>
        <div style='background:#F0F0F0;border-radius:8px;padding:0.6rem;font-size:0.78rem;color:#555;'>
            <b>Bottom-right (Positive + Objective):</b> Balanced good-news reporting
        </div>
        <div style='background:#F0F0F0;border-radius:8px;padding:0.6rem;font-size:0.78rem;color:#555;'>
            <b>Bottom-left (Negative + Objective):</b> Factual negative/critical reporting
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Source ranking ────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Source Reliability Matrix</div>"
                "<div class='section-sub'>Article volume, avg sentiment, and subjectivity per outlet</div>",
                unsafe_allow_html=True)

    src_stats = df.groupby("source").agg(
        Articles=("title", "count"),
        Avg_Sentiment=("compound", "mean"),
        Avg_Subjectivity=("subjectivity", "mean"),
        Positive=("label", lambda x: (x == "positive").sum()),
        Negative=("label", lambda x: (x == "negative").sum()),
    ).round(3).reset_index()
    src_stats.columns = ["Source", "Articles", "Avg Sentiment", "Avg Subjectivity", "Positive", "Negative"]
    src_stats = src_stats.sort_values("Avg Sentiment", ascending=False)

    st.dataframe(
        src_stats.style.background_gradient(subset=["Avg Sentiment"], cmap="RdYlGn")
                       .background_gradient(subset=["Avg Subjectivity"], cmap="Blues"),
        width="stretch",
        hide_index=True,
    )

    st.markdown("---")

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Export Data</div>", unsafe_allow_html=True)

    export_cols = ["title", "source", "published", "label", "compound",
                   "vader_compound", "textblob_polarity", "subjectivity",
                   "pos", "neg", "neu", "url", "summary"]
    export_df = df[[c for c in export_cols if c in df.columns]]

    e1, e2, e3 = st.columns(3)

    with e1:
        csv = export_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV",
            csv, f"newspulse_{category}.csv", "text/csv",
            width="stretch",
        )

    with e2:
        json_str = export_df.to_json(orient="records", indent=2)
        st.download_button(
            "⬇️ Download JSON",
            json_str, f"newspulse_{category}.json", "application/json",
            width="stretch",
        )

    with e3:
        report = f"""NewsPulse Analysis Report
Category: {category.title()}
Articles: {summary['total']}
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

SENTIMENT SUMMARY
-----------------
Positive : {summary['positive']} ({summary['positive']/summary['total']*100:.1f}%)
Neutral  : {summary['neutral']} ({summary['neutral']/summary['total']*100:.1f}%)
Negative : {summary['negative']} ({summary['negative']/summary['total']*100:.1f}%)

Average Compound Score : {summary['avg_compound']:+.4f}
Average Subjectivity   : {summary['avg_subjectivity']:.4f}

TOP POSITIVE HEADLINE
{summary['most_positive']}

TOP NEGATIVE HEADLINE
{summary['most_negative']}
"""
        st.download_button(
            "⬇️ Download Report",
            report, f"newspulse_report_{category}.txt", "text/plain",
            width="stretch",
        )

    st.markdown(f"""
    <div style='margin-top:1rem;background:#F0EDE7;border-radius:8px;padding:0.8rem 1rem;font-size:0.8rem;color:#555;'>
    Export includes {len(export_df)} articles with {len(export_df.columns)} features:
    sentiment labels, VADER scores, TextBlob polarity, subjectivity, source metadata, and URLs.
    </div>
    """, unsafe_allow_html=True)
