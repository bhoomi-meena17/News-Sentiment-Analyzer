"""
utils/nlp.py  —  TF-IDF vectorisation, K-Means clustering, keyword extraction
"""

import re
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize
from collections import Counter


# ── Stopwords (lightweight, no NLTK download needed) ─────────────────────────
STOPWORDS = set("""
a about above after again against all also am an and any are aren't as at be
because been before being below between both but by can't cannot could couldn't
did didn't do does doesn't doing don't down during each few for from further
get got had hadn't has hasn't have haven't having he he'd he'll he's her here
here's hers herself him himself his how how's i i'd i'll i'm i've if in into
is isn't it it's its itself let's me more most mustn't my myself no nor not of
off on once only or other ought our ours ourselves out over own same shan't she
she'd she'll she's should shouldn't so some such than that that's the their
theirs them themselves then there there's these they they'd they'll they're
they've this those through to too under until up very was wasn't we we'd we'll
we're we've were weren't what what's when when's where where's which while who
who's whom why why's will with won't would wouldn't you you'd you'll you're
you've your yours yourself yourselves said new year said also says according
one two three first last report show shows said make made may year years
""".split())


def clean_text(text: str) -> str:
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).lower().strip()
    tokens = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]
    return " ".join(tokens)


def build_tfidf(texts: List[str], max_features: int = 500) -> Tuple:
    cleaned = [clean_text(t) for t in texts]
    vec = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
        sublinear_tf=True,
    )
    try:
        matrix = vec.fit_transform(cleaned)
    except ValueError:
        # fallback without min_df if corpus is tiny
        vec = TfidfVectorizer(max_features=max_features, ngram_range=(1, 2), sublinear_tf=True)
        matrix = vec.fit_transform(cleaned)
    return matrix, vec, cleaned


def cluster_articles(df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
    if len(df) < n_clusters:
        df["cluster"] = 0
        df["cluster_label"] = "General"
        df["pca_x"] = np.random.randn(len(df))
        df["pca_y"] = np.random.randn(len(df))
        return df

    texts = (df["title"] + " " + df["summary"]).fillna("").tolist()
    matrix, vec, _ = build_tfidf(texts)

    # Normalise for cosine distance
    mat_norm = normalize(matrix)

    k = min(n_clusters, len(df) // 3, 8)
    km = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=200)
    labels = km.fit_predict(mat_norm)

    # PCA → 2D for visualisation
    n_components = min(2, mat_norm.shape[1], mat_norm.shape[0])
    pca = PCA(n_components=n_components, random_state=42)
    dense = mat_norm.toarray()
    coords = pca.fit_transform(dense)
    if coords.shape[1] == 1:
        coords = np.hstack([coords, np.zeros((len(coords), 1))])

    # Cluster keywords (top TF-IDF terms per cluster)
    feature_names = np.array(vec.get_feature_names_out())
    cluster_keywords: Dict[int, List[str]] = {}
    for ci in range(k):
        center = km.cluster_centers_[ci]
        top_idx = center.argsort()[-5:][::-1]
        cluster_keywords[ci] = feature_names[top_idx].tolist()

    df = df.copy()
    df["cluster"] = labels
    df["cluster_label"] = df["cluster"].map(
        lambda c: " · ".join(cluster_keywords.get(c, [f"Topic {c}"]))
    )
    df["pca_x"] = coords[:, 0]
    df["pca_y"] = coords[:, 1]
    df["cluster_keywords"] = df["cluster"].map(
        lambda c: cluster_keywords.get(c, [])
    )
    return df


def get_top_keywords(df: pd.DataFrame, n: int = 25) -> Dict[str, int]:
    texts = (df["title"] + " " + df["summary"]).fillna("").tolist()
    all_words: List[str] = []
    for t in texts:
        all_words.extend(clean_text(t).split())
    # Filter single chars
    all_words = [w for w in all_words if len(w) > 3]
    return dict(Counter(all_words).most_common(n))


def get_keywords_by_sentiment(df: pd.DataFrame, label: str, n: int = 15) -> Dict[str, int]:
    sub = df[df["label"] == label]
    return get_top_keywords(sub, n)
