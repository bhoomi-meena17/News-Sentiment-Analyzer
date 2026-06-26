"""
pages/search.py  —  Paste-your-own-text sentiment analyser
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data import vader_sentiment, textblob_sentiment, ensemble_sentiment
import plotly.graph_objects as go


DEMO_TEXTS = {
    "Positive headline": "Scientists make breakthrough discovery that could cure Alzheimer's disease, offering new hope to millions worldwide.",
    "Negative headline": "Markets crash as economic fears grip investors following worse-than-expected jobs data and rising inflation.",
    "Neutral headline": "The Federal Reserve will hold its next policy meeting on Tuesday to discuss interest rate decisions.",
    "Ambiguous": "The new policy has both supporters and critics, with experts divided on its potential long-term impact.",
}


def gauge(value: float, title: str) -> go.Figure:
    color = "#4CAF82" if value >= 0.05 else "#E57373" if value <= -0.05 else "#9BA4B5"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"font": {"size": 28, "color": "#1C1C1E"}, "suffix": ""},
        title={"text": title, "font": {"size": 12, "color": "#6B6B6B"}},
        gauge={
            "axis": {"range": [-1, 1], "tickfont": {"size": 10}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#F8F7F4",
            "bordercolor": "#E8E4DC",
            "steps": [
                {"range": [-1, -0.05], "color": "#FDE8E8"},
                {"range": [-0.05, 0.05], "color": "#F5F5F5"},
                {"range": [0.05, 1],   "color": "#E6F4EA"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.8, "value": value},
        },
    ))
    fig.update_layout(height=200, margin=dict(t=30, b=0, l=20, r=20),
                      paper_bgcolor="#FFFFFF", font=dict(family="Inter"))
    return fig


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>🔍 Analyse Any Text</div>
        <div class='page-tagline'>Paste a headline, article, tweet — get instant multi-model sentiment analysis</div>
    </div>
    """, unsafe_allow_html=True)

    # Demo presets
    st.markdown("**Try a demo:**")
    cols = st.columns(4)
    for i, (k, v) in enumerate(DEMO_TEXTS.items()):
        if cols[i].button(k, width="stretch"):
            st.session_state["search_text"] = v

    text = st.text_area(
        "Enter text to analyse",
        value=st.session_state.get("search_text", ""),
        height=130,
        placeholder="Paste any news headline, article excerpt, or tweet here…",
    )

    if not text.strip():
        st.info("👆 Enter text above or pick a demo to get started.")
        return

    st.markdown("---")

    # ── Three-model comparison ─────────────────────────────────────────────────
    v = vader_sentiment(text)
    t = textblob_sentiment(text)
    e = ensemble_sentiment(text)

    st.markdown("<div class='section-header'>Sentiment Scores</div>", unsafe_allow_html=True)

    g1, g2, g3 = st.columns(3)
    with g1:
        st.plotly_chart(gauge(v["compound"], "VADER"), width="stretch", config={"displayModeBar": False})
        st.markdown(f"<div style='text-align:center;font-size:0.8rem;color:#6B6B6B;'>Pos {v['pos']:.2f} · Neu {v['neu']:.2f} · Neg {v['neg']:.2f}</div>", unsafe_allow_html=True)
    with g2:
        st.plotly_chart(gauge(t["polarity"], "TextBlob"), width="stretch", config={"displayModeBar": False})
        st.markdown(f"<div style='text-align:center;font-size:0.8rem;color:#6B6B6B;'>Subjectivity: {t['subjectivity']:.2f}</div>", unsafe_allow_html=True)
    with g3:
        st.plotly_chart(gauge(e["compound"], "Ensemble (60/40)"), width="stretch", config={"displayModeBar": False})
        label_color = "#1E7A40" if e["label"] == "positive" else "#B91C1C" if e["label"] == "negative" else "#555"
        st.markdown(f"<div style='text-align:center;font-size:0.8rem;color:{label_color};font-weight:600;'>→ {e['label'].upper()}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Detailed breakdown ─────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Detailed Breakdown</div>", unsafe_allow_html=True)

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("**VADER Analysis**")
        for k, val in [("Compound", v["compound"]), ("Positive", v["pos"]),
                       ("Neutral", v["neu"]), ("Negative", v["neg"])]:
            color = "#4CAF82" if val > 0.3 else "#E57373" if (k == "Negative" and val > 0.1) else "#1C1C1E"
            st.markdown(f"<div style='display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #F0EDE7;'>"
                        f"<span style='font-size:0.85rem;color:#6B6B6B;'>{k}</span>"
                        f"<span style='font-size:0.85rem;font-weight:600;color:{color};'>{val:.4f}</span></div>",
                        unsafe_allow_html=True)

    with d2:
        st.markdown("**TextBlob Analysis**")
        for k, val in [("Polarity", t["polarity"]), ("Subjectivity", t["subjectivity"])]:
            st.markdown(f"<div style='display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #F0EDE7;'>"
                        f"<span style='font-size:0.85rem;color:#6B6B6B;'>{k}</span>"
                        f"<span style='font-size:0.85rem;font-weight:600;'>{val:.4f}</span></div>",
                        unsafe_allow_html=True)
        subj_desc = "Very subjective" if t["subjectivity"] > 0.7 else \
                    "Moderately subjective" if t["subjectivity"] > 0.4 else \
                    "Fairly objective"
        st.markdown(f"<div style='margin-top:0.5rem;font-size:0.8rem;color:#8A8A8E;'>→ {subj_desc}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Batch mode ────────────────────────────────────────────────────────────
    with st.expander("📋 Batch Analyse (multiple texts, one per line)"):
        batch_text = st.text_area("Enter texts (one per line)", height=150,
                                   key="batch")
        if st.button("Analyse Batch") and batch_text.strip():
            lines = [l.strip() for l in batch_text.strip().split("\n") if l.strip()]
            results = []
            for line in lines:
                r = ensemble_sentiment(line)
                results.append({"Text": line[:80] + ("…" if len(line) > 80 else ""),
                                 "Sentiment": r["label"].upper(),
                                 "Score": round(r["compound"], 4),
                                 "Subjectivity": round(r["subjectivity"], 4)})
            import pandas as pd
            rdf = pd.DataFrame(results)
            st.dataframe(rdf, width="stretch", hide_index=True)
            csv = rdf.to_csv(index=False)
            st.download_button("⬇️ Download CSV", csv, "batch_sentiment.csv", "text/csv")
