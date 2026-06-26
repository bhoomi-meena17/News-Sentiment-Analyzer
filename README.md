# 📰 NewsPulse — News Sentiment Intelligence Dashboard

> An end-to-end NLP pipeline that fetches live news, scores sentiment with an ensemble model, clusters articles by topic, and visualises everything in a clean Streamlit dashboard.

---

## 🚀 Live Demo

```bash
streamlit run app.py
```

---

## 📌 Project Highlights

| Feature | Details |
|---|---|
| **Live RSS ingestion** | 20+ feeds across 7 categories |
| **Ensemble sentiment** | VADER (60%) + TextBlob (40%) weighted fusion |
| **Topic clustering** | TF-IDF bigrams → K-Means → PCA 2D map |
| **4-page dashboard** | Overview · Analyse · Cluster · Insights |
| **Data export** | CSV / JSON / text report |
| **Zero external API** | Fully offline after pip install |

---

## 🧠 Architecture

```
RSS Feeds (feedparser)
       │
       ▼
  Text Cleaning
       │
       ├──► VADER Sentiment ──┐
       │                      ├──► Ensemble Score → Label
       └──► TextBlob Sentiment┘
                │
                ▼
         TF-IDF Vectoriser (500 bigram features)
                │
                ├──► K-Means Clustering (k=3–10)
                │         │
                │         └──► PCA(2D) → Scatter Plot
                │
                └──► Top Keywords per cluster
                           │
                           ▼
                    Streamlit Dashboard
                    ┌─────────────────────────────┐
                    │ 🏠 Dashboard  (KPIs + feed) │
                    │ 🔍 Search    (any text)     │
                    │ 📊 Clusters  (topic map)    │
                    │ 💡 Insights  (export)       │
                    └─────────────────────────────┘
```

---

## 🛠️ Setup

### 1. Clone / download
```bash
git clone https://github.com/yourname/News-Sentiment-Analyzer.git
cd newspulse
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📁 Project Structure

```
news_sentiment/
├── app.py                  # Entry point — routing + global CSS
├── requirements.txt
├── .streamlit/
│   └── config.toml         # Theme config
├── views/
│   ├── dashboard.py        # Page 1: Live feed overview
│   ├── search.py           # Page 2: Paste-your-own-text analyser
│   ├── clustering.py       # Page 3: TF-IDF + K-Means topic map
│   └── insights.py         # Page 4: Deep-dive + export
└── utils/
    ├── data.py             # RSS fetch, sentiment scoring, caching
    ├── nlp.py             # TF-IDF, K-Means, PCA, keywords
    ├── mock_data.py       #mock data for demo/testing when RSS feeds are blocked
    └── charts.py           # All Plotly chart builders
```

---

## 📊 Features Explained

### 1. 🏠 Dashboard
- KPI metrics: total articles, positive/negative/neutral counts, avg score
- Sentiment donut chart + score histogram
- Publication timeline (stacked daily bar)
- Per-source sentiment bar chart
- Filterable, sortable article feed with inline badges

### 2. 🔍 Search & Analyse
- Analyse any text (headline, tweet, paragraph)
- Three-gauge display: VADER · TextBlob · Ensemble
- Batch mode: paste multiple texts, download CSV results
- Demo presets for instant exploration

### 3. 📊 Topic Clustering
- TF-IDF vectorisation with bigrams (min_df, sublinear_tf)
- K-Means clustering (configurable 3–10 clusters)
- PCA 2D projection for interactive scatter map
- Per-cluster keyword summary + sentiment breakdown
- Top-keyword frequency charts by sentiment

### 4. 💡 Insights & Export
- Narrative insight cards (mood, dominant tone, extremes)
- Subjectivity × Sentiment quadrant scatter
- Source reliability matrix with styled dataframe
- Export: CSV, JSON, or plain-text summary report

---

## 🤖 ML / NLP Pipeline Details

### Sentiment Models

**VADER** (`vaderSentiment`)
- Rule-based lexicon model designed for social/news text
- Outputs: `pos`, `neu`, `neg`, `compound` ∈ [−1, 1]
- Best at: short, punchy headlines

**TextBlob** (`textblob`)
- Pattern-based model with subjectivity scoring
- Outputs: `polarity` ∈ [−1, 1], `subjectivity` ∈ [0, 1]
- Best at: longer, more narrative text

**Ensemble**
```python
compound = 0.6 × vader_compound + 0.4 × textblob_polarity
label = "positive" if compound ≥ 0.05
      = "negative" if compound ≤ −0.05
      = "neutral"
```

### Topic Clustering

```python
TfidfVectorizer(max_features=500, ngram_range=(1,2),
                min_df=2, max_df=0.85, sublinear_tf=True)
→ normalize (L2, cosine distance)
→ KMeans(n_clusters=k, n_init=10)
→ PCA(n_components=2)
```

Top keywords per cluster are extracted from K-Means centroid vectors.

---

## 📈 Extending the Project

| Idea | Difficulty |
|---|---|
| Add transformer model (FinBERT / roBERTa) | Medium |
| Named entity extraction (spaCy) | Easy |
| Topic labelling with LLM | Easy |
| Email alerts for sentiment spikes | Easy |
| Historical trend database (SQLite) | Medium |
| Deploy to Streamlit Cloud | Easy |

---

## 🧰 Tech Stack

| Layer | Library |
|---|---|
| UI / App | Streamlit 1.28+ |
| Data viz | Plotly 5.x |
| Sentiment | VADER, TextBlob |
| Vectorisation | scikit-learn TF-IDF |
| Clustering | scikit-learn K-Means |
| Dimensionality reduction | scikit-learn PCA |
| RSS parsing | feedparser |
| Data wrangling | pandas, numpy |

---

## 👩‍💻 Author

**Bhoomi** — CSAI, NSUT  
Built as an internship-level portfolio project demonstrating NLP, ML pipelines, and production-quality Streamlit development.

---

## 📄 License

MIT — free to use, modify, and deploy.
