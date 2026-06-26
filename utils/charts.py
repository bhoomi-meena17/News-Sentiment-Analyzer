"""
utils/charts.py  —  Plotly chart builders (light palette)
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional

# ── Palette ───────────────────────────────────────────────────────────────────
COLORS = {
    "positive": "#4CAF82",
    "neutral":  "#9BA4B5",
    "negative": "#E57373",
    "bg":       "#FFFFFF",
    "grid":     "#F0EDE7",
    "text":     "#1C1C1E",
    "subtext":  "#8A8A8E",
    "accent":   "#5B7FDE",
    "accent2":  "#E8883A",
}

LABEL_COLORS = {
    "positive": COLORS["positive"],
    "neutral":  COLORS["neutral"],
    "negative": COLORS["negative"],
}

BASE_LAYOUT = dict(
    paper_bgcolor=COLORS["bg"],
    plot_bgcolor=COLORS["bg"],
    font=dict(family="Inter, sans-serif", color=COLORS["text"], size=12),
    margin=dict(t=30, b=20, l=10, r=10),
    showlegend=True,
)


def _apply_base(fig: go.Figure, height: int = 320) -> go.Figure:
    fig.update_layout(**BASE_LAYOUT, height=height)
    fig.update_xaxes(showgrid=True, gridcolor=COLORS["grid"], zeroline=False,
                     tickfont=dict(size=11, color=COLORS["subtext"]))
    fig.update_yaxes(showgrid=True, gridcolor=COLORS["grid"], zeroline=False,
                     tickfont=dict(size=11, color=COLORS["subtext"]))
    return fig


# ── Charts ────────────────────────────────────────────────────────────────────

def sentiment_donut(df: pd.DataFrame) -> go.Figure:
    counts = df["label"].value_counts()
    labels = list(counts.index)
    values = list(counts.values)
    colors = [LABEL_COLORS.get(l, "#ccc") for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="percent+label",
        textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
    ))
    avg = df["compound"].mean()
    fig.add_annotation(
        text=f"<b>{avg:+.2f}</b><br><span style='font-size:10px;color:#8A8A8E'>Avg Score</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(size=16), align="center",
    )
    fig.update_layout(**BASE_LAYOUT, height=300,
                      legend=dict(orientation="h", yanchor="bottom", y=-0.15, x=0.5, xanchor="center"))
    return fig


def compound_histogram(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for label, color in LABEL_COLORS.items():
        sub = df[df["label"] == label]["compound"]
        if sub.empty:
            continue
        fig.add_trace(go.Histogram(
            x=sub, name=label.capitalize(),
            marker_color=color, opacity=0.78,
            nbinsx=20, hovertemplate=f"{label}: %{{x:.2f}}<extra></extra>",
        ))
    fig.update_layout(barmode="overlay", **BASE_LAYOUT, height=280,
                      legend=dict(orientation="h", y=1.05))
    fig.update_xaxes(title_text="Sentiment Score", gridcolor=COLORS["grid"])
    fig.update_yaxes(title_text="Articles", gridcolor=COLORS["grid"])
    return _apply_base(fig, 280)


def sentiment_by_source(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby("source")["compound"].agg(["mean", "count"]).reset_index()
    grp.columns = ["source", "avg_score", "count"]
    grp = grp.sort_values("avg_score")

    colors = [LABEL_COLORS["positive"] if s >= 0.05 else
              LABEL_COLORS["negative"] if s <= -0.05 else
              LABEL_COLORS["neutral"] for s in grp["avg_score"]]

    fig = go.Figure(go.Bar(
        y=grp["source"], x=grp["avg_score"],
        orientation="h",
        marker=dict(color=colors, line=dict(color="white", width=0.5)),
        text=[f"{s:+.2f}  ({c} articles)" for s, c in zip(grp["avg_score"], grp["count"])],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Avg Score: %{x:.3f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_dash="dash", line_color=COLORS["subtext"], line_width=1)
    fig.update_layout(**BASE_LAYOUT, height=max(260, len(grp) * 38))
    fig.update_xaxes(title_text="Average Compound Score", gridcolor=COLORS["grid"])
    return fig


def subjectivity_scatter(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df, x="compound", y="subjectivity",
        color="label",
        color_discrete_map=LABEL_COLORS,
        hover_data={"title": True, "source": True, "compound": ":.3f", "subjectivity": ":.3f"},
        labels={"compound": "Sentiment Score", "subjectivity": "Subjectivity"},
        opacity=0.75,
    )
    fig.update_traces(marker=dict(size=7, line=dict(color="white", width=0.5)))
    fig.add_vline(x=0, line_dash="dot", line_color=COLORS["subtext"], line_width=1)
    fig.add_hline(y=0.5, line_dash="dot", line_color=COLORS["subtext"], line_width=1)
    fig.update_layout(**BASE_LAYOUT, height=340,
                      legend=dict(orientation="h", y=1.05))
    return _apply_base(fig, 340)


def cluster_bubble(df: pd.DataFrame) -> go.Figure:
    """2-D scatter of PCA-reduced TF-IDF, coloured by cluster."""
    if "pca_x" not in df.columns:
        return go.Figure()
    unique_clusters = df["cluster"].unique()
    palette = px.colors.qualitative.Pastel
    fig = go.Figure()
    for i, c in enumerate(sorted(unique_clusters)):
        sub = df[df["cluster"] == c]
        label_name = sub["cluster_label"].iloc[0] if "cluster_label" in sub.columns else f"Topic {c}"
        fig.add_trace(go.Scatter(
            x=sub["pca_x"], y=sub["pca_y"],
            mode="markers",
            name=label_name,
            marker=dict(
                size=9, color=palette[i % len(palette)],
                line=dict(color="white", width=0.8), opacity=0.82,
            ),
            hovertemplate="<b>%{customdata[0]}</b><br>Source: %{customdata[1]}<br>Sentiment: %{customdata[2]:.3f}<extra></extra>",
            customdata=sub[["title", "source", "compound"]].values,
        ))
    fig.update_layout(**BASE_LAYOUT, height=380,
                      legend=dict(orientation="v", x=1.01, y=1))
    return _apply_base(fig, 380)


def top_words_bar(word_freq: dict, title: str = "Top Keywords", n: int = 15) -> go.Figure:
    words = list(word_freq.keys())[:n]
    freqs = list(word_freq.values())[:n]
    fig = go.Figure(go.Bar(
        y=words[::-1], x=freqs[::-1], orientation="h",
        marker=dict(
            color=freqs[::-1],
            colorscale=[[0, "#D6E4F7"], [1, COLORS["accent"]]],
            showscale=False,
        ),
        hovertemplate="%{y}: %{x}<extra></extra>",
    ))
    fig.update_layout(**BASE_LAYOUT, height=max(240, n * 26), title_text=title,
                      title_font=dict(size=13))
    return _apply_base(fig, max(240, n * 26))


def timeline_bar(df: pd.DataFrame) -> go.Figure:
    """Stacked daily bar of sentiment counts."""
    df2 = df.copy()
    df2["date"] = pd.to_datetime(df2["published"], errors="coerce").dt.date
    grp = df2.groupby(["date", "label"]).size().reset_index(name="count")
    fig = go.Figure()
    for label, color in LABEL_COLORS.items():
        sub = grp[grp["label"] == label]
        fig.add_trace(go.Bar(
            x=sub["date"], y=sub["count"], name=label.capitalize(),
            marker_color=color, opacity=0.85,
        ))
    fig.update_layout(barmode="stack", **BASE_LAYOUT, height=260,
                      legend=dict(orientation="h", y=1.08))
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Articles")
    return _apply_base(fig, 260)
