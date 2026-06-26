"""
utils/data.py  —  Feed fetching, sentiment scoring, caching
"""

import feedparser
import pandas as pd
import hashlib
import time
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional

import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

# ── RSS feed catalogue ─────────────────────────────────────────────────────────
FEEDS: Dict[str, List[str]] = {
    "technology": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.wired.com/feed/rss",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.theverge.com/rss/index.xml",
    ],
    "business": [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://www.ft.com/rss/home/uk",
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    ],
    "science": [
        "https://www.sciencedaily.com/rss/all.xml",
        "https://feeds.newscientist.com/full-feed",
        "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
    ],
    "health": [
        "https://rss.medicalnewstoday.com/featurednews.xml",
        "https://www.who.int/rss-feeds/news-english.xml",
        "https://www.healthline.com/rss/news",
    ],
    "entertainment": [
        "https://variety.com/feed/",
        "https://deadline.com/feed/",
        "https://www.hollywoodreporter.com/feed/",
    ],
    "sports": [
        "https://www.espn.com/espn/rss/news",
        "https://sports.yahoo.com/rss/",
        "https://www.skysports.com/rss/12040",
    ],
    "world": [
        "https://feeds.reuters.com/Reuters/worldNews",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
    ],
}

_vader = SentimentIntensityAnalyzer()


# ── Sentiment helpers ──────────────────────────────────────────────────────────

def vader_sentiment(text: str) -> Dict:
    scores = _vader.polarity_scores(text)
    label = "positive" if scores["compound"] >= 0.05 else \
            "negative" if scores["compound"] <= -0.05 else "neutral"
    return {"compound": scores["compound"], "label": label,
            "pos": scores["pos"], "neg": scores["neg"], "neu": scores["neu"]}


def textblob_sentiment(text: str) -> Dict:
    blob = TextBlob(text)
    pol = blob.sentiment.polarity
    sub = blob.sentiment.subjectivity
    label = "positive" if pol > 0.05 else "negative" if pol < -0.05 else "neutral"
    return {"polarity": pol, "subjectivity": sub, "label": label}


def ensemble_sentiment(text: str) -> Dict:
    v = vader_sentiment(text)
    t = textblob_sentiment(text)
    # Weighted average: 60% VADER, 40% TextBlob
    compound = 0.6 * v["compound"] + 0.4 * t["polarity"]
    label = "positive" if compound >= 0.05 else \
            "negative" if compound <= -0.05 else "neutral"
    return {
        "compound": round(compound, 4),
        "label": label,
        "vader_compound": v["compound"],
        "textblob_polarity": t["polarity"],
        "subjectivity": t["subjectivity"],
        "pos": v["pos"], "neg": v["neg"], "neu": v["neu"],
    }


def clean_html(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = re.sub(r"&[a-z]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# ── RSS fetching ───────────────────────────────────────────────────────────────

def _parse_date(entry) -> Optional[datetime]:
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def _fetch_single_feed(url: str, max_items: int = 30) -> List[Dict]:
    try:
        feed = feedparser.parse(url, agent="NewsPulse/1.0")
        articles = []
        for entry in feed.entries[:max_items]:
            title = clean_html(getattr(entry, "title", "") or "")
            summary = clean_html(getattr(entry, "summary", "") or
                                  getattr(entry, "description", "") or "")
            if not title:
                continue
            text = f"{title}. {summary}"
            sentiment = ensemble_sentiment(text)
            pub = _parse_date(entry)
            articles.append({
                "title": title,
                "summary": summary[:300] if summary else "",
                "url": getattr(entry, "link", ""),
                "source": feed.feed.get("title", url.split("/")[2]),
                "published": pub.strftime("%Y-%m-%d %H:%M") if pub else "Unknown",
                "published_dt": pub,
                **sentiment,
                "text": text,
                "word_count": len(text.split()),
            })
        return articles
    except Exception:
        return []


@st.cache_data(ttl=600, show_spinner=False)
def fetch_articles(category: str, max_total: int = 50) -> pd.DataFrame:
    urls = FEEDS.get(category, FEEDS["technology"])
    per_feed = max(10, max_total // len(urls))
    all_articles: List[Dict] = []
    for url in urls:
        all_articles.extend(_fetch_single_feed(url, per_feed))

    if not all_articles:
        # Fallback to curated demo data (useful for offline/demo environments)
        from utils.mock_data import get_mock_data
        return get_mock_data(category, max_total)

    df = pd.DataFrame(all_articles)
    # Deduplicate by title hash
    df["_hash"] = df["title"].apply(lambda t: hashlib.md5(t.encode()).hexdigest())
    df = df.drop_duplicates(subset="_hash").drop(columns="_hash")
    df = df.sort_values("published_dt", ascending=False, na_position="last")
    df = df.head(max_total).reset_index(drop=True)
    return df


def get_sentiment_summary(df: pd.DataFrame) -> Dict:
    if df.empty:
        return {}
    counts = df["label"].value_counts()
    total = len(df)
    return {
        "total": total,
        "positive": int(counts.get("positive", 0)),
        "negative": int(counts.get("negative", 0)),
        "neutral": int(counts.get("neutral", 0)),
        "avg_compound": round(df["compound"].mean(), 4),
        "avg_subjectivity": round(df["subjectivity"].mean(), 4),
        "most_positive": df.loc[df["compound"].idxmax(), "title"] if total else "",
        "most_negative": df.loc[df["compound"].idxmin(), "title"] if total else "",
    }
