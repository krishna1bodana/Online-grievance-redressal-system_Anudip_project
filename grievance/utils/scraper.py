import os
import re
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

# ---------------- PRIORITY ANALYSIS ----------------
def analyze_grievance_text(text):
    """
    Analyze grievance text and return suggested priority
    based on presence of critical keywords.
    """
    if not text:
        return 'Low'

    urgent_keywords = [
        'corruption', 'bribe', 'delay', 'emergency',
        'harassment', 'fraud', 'complaint', 'illegal',
        'urgent', 'immediate', 'threat', 'safety'
    ]

    score = 0
    text_lower = text.lower()

    for word in urgent_keywords:
        # Proper word-boundary check using regex
        if re.search(rf'\b{re.escape(word)}\b', text_lower):
            score += 1

    if score >= 3:
        return 'High'
    elif score >= 1:
        return 'Medium'
    return 'Low'


# ---------------- RELATED NEWS ----------------
def fetch_related_news(category_name):
    """
    Fetch related news articles based on grievance category
    using NewsAPI. Returns a list of articles or an empty list.
    """
    API_KEY = os.getenv('NEWS_API_KEY')

    if not API_KEY or not category_name:
        return []

    url = (
        "https://newsapi.org/v2/everything"
        f"?q={category_name}&pageSize=5&apiKey={API_KEY}"
    )

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'ok':
            return data.get('articles', [])
        return []

    except requests.RequestException as e:
        logger.error(
            "News API error for category '%s': %s",
            category_name,
            e
        )
        return []


# ---------------- OPTIONAL SCRAPING ----------------
def scrape_official_guidelines(topic):
    """
    OPTIONAL utility example.
    Scrapes a government portal for guidelines related to a topic.
    Returns a small list of titles or an empty list on failure.
    """
    if not topic:
        return []

    search_url = f"https://www.example-gov-portal.in/search?q={topic}"

    try:
        response = requests.get(search_url, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Placeholder selector — adjust per real site
        links = soup.select('.search-result-link')

        return [link.get_text(strip=True) for link in links[:3]]

    except requests.RequestException as e:
        logger.warning(
            "Guideline scraping failed for topic '%s': %s",
            topic,
            e
        )
        return []
# =========================
# END OF FILE