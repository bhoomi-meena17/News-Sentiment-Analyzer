"""
pages/clustering.py  —  TF-IDF + K-Means topic clustering + word cloud
"""

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data import fetch_articles
from utils.nlp import cluster_articles, get_top_keywords, get_keywords_by_sentiment
from utils import charts


def render(category: str, num_articles: int, refresh: bool):
    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>📊 Topic Clustering</div>
        <div class='page-tagline'>Unsupervised discovery of news themes via TF-IDF & K-Means</div>
    </div>
    """, unsafe_allow_html=True)

    if refresh:
        st.cache_data.clear()

    with st.spinner("Vectorising and clustering articles…"):
        df = fetch_articles(category, num_articles)

    if df.empty:
        st.warning("No articles available. Try refreshing or changing category.")
        return

    # Params
    p1, p2 = st.columns([1, 2])
    with p1:
        n_clusters = st.slider("Number of topic clusters", 3, min(10, len(df)//4+2), 5)
    with p2:
        st.markdown("""
        <div style='background:#F0EDE7;border-radius:8px;padding:0.7rem 1rem;font-size:0.8rem;color:#555;margin-top:0.5rem;'>
        <b>How it works:</b> Article titles + summaries are vectorised with TF-IDF (bigrams, 500 features),
        then grouped with K-Means. PCA reduces to 2D for the scatter plot.
        </div>
        """, unsafe_allow_html=True)

    with st.spinner("Running clustering…"):
        cdf = cluster_articles(df, n_clusters)

    st.session_state["df"] = cdf

    # ── Cluster scatter ────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Article Cluster Map</div>"
                "<div class='section-sub'>Each dot is an article; colour = topic cluster</div>", unsafe_allow_html=True)
    st.plotly_chart(charts.cluster_bubble(cdf), width="stretch",
                    config={"displayModeBar": False})

    st.markdown("---")

    # ── Per-cluster breakdown ──────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Cluster Breakdown</div>", unsafe_allow_html=True)

    unique_clusters = sorted(cdf["cluster"].unique())
    tabs = st.tabs([f"Topic {c+1}" for c in unique_clusters])

    for tab, cluster_id in zip(tabs, unique_clusters):
        with tab:
            sub = cdf[cdf["cluster"] == cluster_id]
            keywords = sub["cluster_keywords"].iloc[0] if "cluster_keywords" in sub.columns else []
            kw_str = " · ".join(f"**{k}**" for k in keywords) if keywords else "—"

            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"**Keywords:** {kw_str}")
                st.markdown(f"**Articles:** {len(sub)}")
                counts = sub["label"].value_counts()
                total = len(sub)
                for lbl, clr in [("positive", "#1E7A40"), ("neutral", "#555"), ("negative", "#B91C1C")]:
                    n = int(counts.get(lbl, 0))
                    pct = n / total * 100 if total else 0
                    st.markdown(
                        f"<div style='font-size:0.82rem;color:{clr};'>● {lbl.capitalize()}: {n} ({pct:.0f}%)</div>",
                        unsafe_allow_html=True
                    )
                avg = sub["compound"].mean()
                mood = "📈 Positive lean" if avg > 0.05 else "📉 Negative lean" if avg < -0.05 else "➡️ Neutral"
                st.markdown(f"<div style='margin-top:0.5rem;font-size:0.82rem;color:#6B6B6B;'>{mood} ({avg:+.3f})</div>",
                            unsafe_allow_html=True)

            with c2:
                for _, row in sub.head(6).iterrows():
                    badge_color = "#E6F4EA" if row["label"] == "positive" else \
                                  "#FDE8E8" if row["label"] == "negative" else "#F5F5F5"
                    txt_color = "#1E7A40" if row["label"] == "positive" else \
                                "#B91C1C" if row["label"] == "negative" else "#555"
                    url_open = f'<a href="{row["url"]}" target="_blank" style="text-decoration:none;color:inherit;">' if row.get("url") else ""
                    url_close = "</a>" if row.get("url") else ""
                    st.markdown(f"""
                    <div style='border-left:3px solid {badge_color.replace("0.1","1")};
                         background:{badge_color};border-radius:0 6px 6px 0;
                         padding:0.5rem 0.8rem;margin-bottom:0.4rem;'>
                        <div style='font-size:0.83rem;font-weight:600;color:#1C1C1E;'>{url_open}{row['title']}{url_close}</div>
                        <div style='font-size:0.73rem;color:{txt_color};margin-top:2px;'>{row['compound']:+.3f} · {row.get('source','?')}</div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Keyword frequency ─────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Keyword Frequency</div>", unsafe_allow_html=True)

    kf1, kf2, kf3 = st.columns(3)
    with kf1:
        kw_all = get_top_keywords(cdf, 15)
        st.plotly_chart(charts.top_words_bar(kw_all, "All Articles", 15),
                        width="stretch", config={"displayModeBar": False})
    with kf2:
        kw_pos = get_keywords_by_sentiment(cdf, "positive", 12)
        st.plotly_chart(charts.top_words_bar(kw_pos, "Positive Articles", 12),
                        width="stretch", config={"displayModeBar": False})
    with kf3:
        kw_neg = get_keywords_by_sentiment(cdf, "negative", 12)
        st.plotly_chart(charts.top_words_bar(kw_neg, "Negative Articles", 12),
                        width="stretch", config={"displayModeBar": False})
