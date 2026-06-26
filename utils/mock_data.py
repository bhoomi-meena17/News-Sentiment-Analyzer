"""
utils/mock_data.py  —  Realistic demo data for offline/demo mode
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

MOCK_ARTICLES = {
    "technology": [
        ("OpenAI launches GPT-5 with unprecedented reasoning abilities", "The latest model from OpenAI demonstrates advanced multi-step reasoning across math, coding, and science, outperforming human experts on key benchmarks.", "positive", "TechCrunch", "https://techcrunch.com"),
        ("Apple faces antitrust investigation over App Store policies", "European regulators have opened a formal probe into Apple's App Store commission structure, citing anti-competitive behaviour that harms developers.", "negative", "The Verge", "https://theverge.com"),
        ("Meta announces layoffs affecting 5% of workforce amid restructuring", "Meta Platforms confirmed plans to reduce its global headcount by approximately 5%, focusing cuts on middle management and non-technical roles.", "negative", "Reuters", "https://reuters.com"),
        ("Google DeepMind AlphaFold breakthrough maps every known protein", "Researchers at DeepMind have extended AlphaFold to predict protein interactions at scale, a development scientists call transformative for drug discovery.", "positive", "Nature News", "https://nature.com"),
        ("Microsoft integrates Copilot AI across all Office 365 products", "The deep integration of AI assistance into Word, Excel, and Outlook is now rolling out to all enterprise customers, Microsoft announced at its developer conference.", "positive", "Wired", "https://wired.com"),
        ("Semiconductor shortage eases as TSMC expands capacity in Arizona", "Taiwan Semiconductor Manufacturing Company's new Arizona fab has come online, providing relief to automotive and consumer electronics supply chains.", "positive", "Bloomberg", "https://bloomberg.com"),
        ("Cybersecurity breach exposes data of 40 million T-Mobile customers", "T-Mobile disclosed a significant data breach affecting tens of millions of current and former customers, exposing names, addresses, and partial financial information.", "negative", "Ars Technica", "https://arstechnica.com"),
        ("Netflix tests AI-generated subtitles in 12 new languages", "The streaming giant is piloting machine-translated subtitles powered by its in-house AI models, potentially expanding accessibility to underserved markets.", "neutral", "Variety", "https://variety.com"),
        ("SpaceX Starship completes first orbital flight successfully", "SpaceX's massive Starship vehicle completed a full orbital mission and returned to the launch site for a precision catch, marking a milestone in reusable rocketry.", "positive", "Ars Technica", "https://arstechnica.com"),
        ("TikTok faces potential ban in three more European Union member states", "Following national security reviews, France, Germany, and the Netherlands are considering legislation that would restrict TikTok's operations within their borders.", "negative", "Reuters", "https://reuters.com"),
        ("AMD's new Ryzen AI chips outperform Intel in laptop efficiency tests", "Independent benchmarks show AMD's latest mobile processors deliver higher performance per watt, posing a serious challenge to Intel's market leadership.", "positive", "AnandTech", "https://anandtech.com"),
        ("GitHub Copilot adoption surpasses one million enterprise users", "Microsoft's AI coding assistant has crossed a major milestone in enterprise adoption, with users reporting 35–55% productivity gains on repetitive coding tasks.", "positive", "TechCrunch", "https://techcrunch.com"),
        ("Uber and Lyft challenge new gig worker law in California court", "Both ridesharing companies are contesting a state ruling that would classify their drivers as employees, citing potential cost increases that could end operations.", "negative", "The Verge", "https://theverge.com"),
        ("Samsung unveils foldable laptop with OLED display at CES", "Samsung's new Galaxy Book Fold features a 17-inch OLED screen that folds to tablet size, with the company targeting creative professionals and executives.", "positive", "CNET", "https://cnet.com"),
        ("EU AI Act enforcement begins: major tech firms scramble to comply", "With the first enforcement deadline now active, Google, Meta, and Amazon are racing to update their AI systems to meet transparency and risk management requirements.", "neutral", "Wired", "https://wired.com"),
    ],
    "business": [
        ("Federal Reserve holds rates steady amid mixed economic signals", "The Federal Open Market Committee voted unanimously to maintain the federal funds rate, citing cooling inflation but persistent labour market strength.", "neutral", "Bloomberg", "https://bloomberg.com"),
        ("S&P 500 reaches record high driven by tech rally", "Strong earnings from the largest technology companies propelled the S&P 500 index to a new all-time high, with the index gaining 2.3% on the week.", "positive", "CNBC", "https://cnbc.com"),
        ("JPMorgan warns of recession risk rising to 40% by end of year", "The investment bank's chief economist cited declining consumer confidence, tightening credit conditions, and global trade uncertainty as primary risk factors.", "negative", "Financial Times", "https://ft.com"),
        ("Amazon Prime Day 2026 breaks all-time sales record", "Amazon reported record-breaking sales during its annual Prime Day event, with third-party seller revenue up 28% year-over-year across 27 countries.", "positive", "Reuters", "https://reuters.com"),
        ("Boeing 737 MAX recertification stalls as new defects found", "Federal Aviation Administration inspectors discovered additional manufacturing irregularities in Boeing's flagship narrowbody aircraft, delaying recertification.", "negative", "Bloomberg", "https://bloomberg.com"),
        ("Inflation falls to 2.1%, nearing central bank target", "The latest consumer price index reading showed headline inflation continuing its decline, raising expectations of a rate cut at the next Fed meeting.", "positive", "CNBC", "https://cnbc.com"),
        ("NVIDIA market cap briefly surpasses Apple for second time", "Driven by insatiable AI chip demand, NVIDIA briefly eclipsed Apple as the world's most valuable company before markets pulled back late in the session.", "positive", "Financial Times", "https://ft.com"),
        ("Starbucks announces 1,500 store closures in cost-cutting drive", "The coffee chain's new leadership team unveiled a sweeping restructuring that will close underperforming locations and reduce corporate headcount globally.", "negative", "Reuters", "https://reuters.com"),
    ],
    "health": [
        ("Breakthrough mRNA vaccine shows 94% efficacy against flu strains", "Clinical trial results published in the New England Journal of Medicine demonstrate that the next-generation flu vaccine offers substantially improved protection.", "positive", "Medical News Today", "https://medicalnewstoday.com"),
        ("WHO declares end of mpox public health emergency", "The World Health Organisation announced that monkeypox no longer meets the criteria for a public health emergency of international concern.", "positive", "WHO", "https://who.int"),
        ("New study links ultra-processed food consumption to depression risk", "A large-scale cohort study of over 200,000 participants found that high intake of ultra-processed foods was associated with a 23% increased risk of depression.", "negative", "New Scientist", "https://newscientist.com"),
        ("Ozempic shortages worsen as demand for weight-loss drugs surges", "Supply chain constraints for GLP-1 agonist medications have intensified, leaving many diabetic patients unable to access their prescribed treatments.", "negative", "Healthline", "https://healthline.com"),
        ("Alzheimer's drug trial shows significant cognitive decline reduction", "Phase III trial data for a novel anti-amyloid therapy shows a 35% reduction in cognitive decline rate over 18 months, offering renewed hope to patients.", "positive", "Medical News Today", "https://medicalnewstoday.com"),
    ],
    "world": [
        ("UN climate summit reaches landmark agreement on emissions targets", "Nations representing 85% of global emissions endorsed a new framework committing to net-zero carbon by 2055, with binding interim milestones.", "positive", "Al Jazeera", "https://aljazeera.com"),
        ("Ukraine-Russia peace talks resume in Istanbul", "Delegations from both countries met for the first substantive negotiations in over a year, with mediators reporting cautious progress on prisoner exchange agreements.", "neutral", "Reuters", "https://reuters.com"),
        ("Devastating earthquake strikes Turkey and Syria, thousands feared dead", "A magnitude 7.6 earthquake struck the border region late at night, causing widespread building collapses and triggering international rescue operations.", "negative", "Al Jazeera", "https://aljazeera.com"),
        ("India overtakes Japan as world's fourth largest economy", "IMF data confirms that India's GDP has surpassed Japan's in nominal dollar terms, marking a historic shift in the global economic order.", "positive", "Reuters", "https://reuters.com"),
        ("G7 agrees on new sanctions targeting Russian energy revenues", "Leaders of the world's seven largest democracies agreed to a new sanctions package targeting shadow fleet oil tankers and Russian energy infrastructure.", "negative", "Financial Times", "https://ft.com"),
    ],
    "science": [
        ("James Webb Space Telescope discovers oldest galaxy ever observed", "Astronomers using JWST data have confirmed the detection of a galaxy that formed just 290 million years after the Big Bang, rewriting our understanding of early cosmic history.", "positive", "Science Daily", "https://sciencedaily.com"),
        ("Scientists achieve stable nuclear fusion reaction for 8 minutes", "Researchers at a UK government fusion facility sustained a plasma reaction far longer than previously achieved, a critical step toward commercial fusion power.", "positive", "New Scientist", "https://newscientist.com"),
        ("Deep sea mining approved despite marine biologist protests", "International Seabed Authority has approved commercial deep-sea mining licenses in the Pacific despite significant opposition from conservation scientists.", "negative", "Science Daily", "https://sciencedaily.com"),
        ("CRISPR therapy cures sickle cell disease in 15-year study", "Long-term follow-up data for the first cohort of patients who received gene editing treatment shows complete or near-complete resolution of sickle cell disease symptoms.", "positive", "New Scientist", "https://newscientist.com"),
    ],
}

# Merge all into one pool for generic category
MOCK_ARTICLES["entertainment"] = [
    ("Cannes Palme d'Or winner breaks streaming records on Netflix", "The acclaimed French drama that won the top prize at Cannes has become Netflix's most-watched non-English film in its first 10 days of availability.", "positive", "Variety", "https://variety.com"),
    ("Taylor Swift Eras Tour film crosses $1 billion at global box office", "The concert film documenting Swift's record-breaking world tour has become the highest-grossing concert film in cinema history.", "positive", "Hollywood Reporter", "https://hollywoodreporter.com"),
    ("Hollywood writers strike looms as contract negotiations collapse", "The Writers Guild of America has authorised strike action after contract talks with the major studios broke down over AI usage and residual payment disputes.", "negative", "Deadline", "https://deadline.com"),
]
MOCK_ARTICLES["sports"] = [
    ("Lionel Messi wins record eighth Ballon d'Or at age 38", "Argentine superstar Lionel Messi claimed his eighth Ballon d'Or award in a ceremony in Paris, extending his own record as the greatest of all time.", "positive", "Sky Sports", "https://skysports.com"),
    ("NBA Finals: Boston Celtics defeat Denver Nuggets in seven games", "The Celtics claimed their 18th championship in a thrilling seven-game series, with Jayson Tatum earning Finals MVP honours.", "positive", "ESPN", "https://espn.com"),
    ("World Athletics doping scandal rocks sprinting events", "Three gold medallists from the previous World Championships have been stripped of their titles following a major anti-doping investigation.", "negative", "Sky Sports", "https://skysports.com"),
]


def get_mock_data(category: str = "technology", n: int = 40) -> pd.DataFrame:
    articles = MOCK_ARTICLES.get(category, MOCK_ARTICLES["technology"])
    
    rows = []
    base_time = datetime.now()
    rng = np.random.default_rng(42)
    
    for i, (title, summary, label, source, url) in enumerate(articles):
        # Add small compound noise
        base_compound = 0.55 if label == "positive" else -0.45 if label == "negative" else 0.02
        compound = float(np.clip(base_compound + rng.normal(0, 0.08), -1, 1))
        subjectivity = float(np.clip(rng.uniform(0.2, 0.75), 0, 1))
        
        hours_ago = rng.integers(0, 72)
        pub_dt = base_time - timedelta(hours=int(hours_ago))
        
        rows.append({
            "title": title,
            "summary": summary,
            "url": url,
            "source": source,
            "published": pub_dt.strftime("%Y-%m-%d %H:%M"),
            "published_dt": pub_dt,
            "compound": round(compound, 4),
            "label": label,
            "vader_compound": round(compound + rng.normal(0, 0.05), 4),
            "textblob_polarity": round(compound * 0.8 + rng.normal(0, 0.1), 4),
            "subjectivity": round(subjectivity, 4),
            "pos": round(max(0, compound) * 0.6 + rng.uniform(0, 0.1), 3),
            "neg": round(max(0, -compound) * 0.6 + rng.uniform(0, 0.1), 3),
            "neu": round(rng.uniform(0.4, 0.7), 3),
            "text": title + ". " + summary,
            "word_count": len((title + " " + summary).split()),
        })
    
    df = pd.DataFrame(rows)
    # Pad to n with slight variations
    while len(df) < n:
        extra = df.sample(min(len(df), n - len(df)), replace=True, random_state=len(df)).copy()
        extra["compound"] = extra["compound"] + rng.normal(0, 0.06, len(extra))
        extra["compound"] = extra["compound"].clip(-1, 1)
        extra["label"] = extra["compound"].apply(
            lambda c: "positive" if c >= 0.05 else "negative" if c <= -0.05 else "neutral"
        )
        df = pd.concat([df, extra], ignore_index=True)
    
    return df.head(n).reset_index(drop=True)
