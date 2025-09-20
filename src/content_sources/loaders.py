"""
Loaders: web scraping, RSS, PDF loaders, DB connectors.
Keep them small, return dicts with {id, text, metadata}.
"""
from typing import Dict, Any, List
from src.ingestion.preprocess import clean_html_text
import requests
from bs4 import BeautifulSoup
import uuid

def load_from_url(url: str) -> Dict[str, Any]:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(separator="\n")
    clean = clean_html_text(text)
    return {
        "id": str(uuid.uuid4()),
        "source_url": url,
        "text": clean,
        "metadata": {"source": url}
    }

def load_from_rss(rss_url: str) -> List[Dict]:
    # Minimal: parse feed with requests + bs4 or feedparser (not added here)
    import feedparser
    feed = feedparser.parse(rss_url)
    results = []
    for entry in feed.entries:
        results.append({
            "id": str(uuid.uuid4()),
            "source_url": entry.link,
            "text": entry.get("summary", entry.get("title", "")),
            "metadata": {"title": entry.get("title"), "published": entry.get("published")}
        })
    return results

# Add PDF loaders, DB loaders etc.
