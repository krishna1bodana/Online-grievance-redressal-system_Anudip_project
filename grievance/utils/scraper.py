import os
import re
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

# ---------------- PRIORITY ANALYSIS ----------------
def analyze_grievance_text(text):
    """
    Analyze grievance text and return suggested priority based on 
    weighted critical keywords.
    """
    if not text:
        return 'Low'

    # Using weights: Serious issues get higher points
    keywords = {
        'urgent': 2, 'immediate': 2, 'safety': 3, 'threat': 3,
        'emergency': 3, 'illegal': 2, 'corruption': 3, 'bribe': 3,
        'harassment': 3, 'fraud': 2, 'delay': 1, 'complaint': 1
    }

    score = 0
    text_lower = text.lower()

    for word, weight in keywords.items():
        if re.search(rf'\b{re.escape(word)}\b', text_lower):
            score += weight

    if score >= 5:
        return 'High'
    elif score >= 2:
        return 'Medium'
    return 'Low'


# ---------------- RELATED NEWS ----------------
def fetch_related_news(category_name):
    """
    Fetch related news articles using NewsAPI.
    Added User-Agent header to prevent 403 blocks.
    """
    API_KEY = os.getenv('NEWS_API_KEY')
    
    if not API_KEY or not category_name:
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        'q': category_name,
        'pageSize': 5,
        'apiKey': API_KEY,
        'language': 'en',
        'sortBy': 'publishedAt'
    }
    
    headers = {
        'User-Agent': 'GrievancePortal/1.0 (Django Project)'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'ok':
            return data.get('articles', [])
        return []

    except requests.RequestException as e:
        logger.error(f"News API error for {category_name}: {e}")
        return []


# ---------------- OPTIONAL SCRAPING ----------------
def scrape_official_guidelines(topic):
    """
    Utility to scrape government portals for guidelines.
    Enhanced with browser-like headers.
    """
    if not topic:
        return []

    # Example: Searching a public help portal
    search_url = f"https://www.usa.gov/search?query={topic}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=7)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # We look for common result patterns (adjust selectors to your target site)
        results = []
        for item in soup.select('h3')[:3]:  # Usually search results use H3 for titles
            title = item.get_text(strip=True)
            if title:
                results.append(title)
        
        return results

    except requests.RequestException as e:
        logger.warning(f"Scraping failed for topic '{topic}': {e}")
        return []