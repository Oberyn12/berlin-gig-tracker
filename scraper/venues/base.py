"""
Shared types and HTTP client for all venue scrapers.
"""
from __future__ import annotations

import httpx

# Shared headers that look like a regular browser request
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Mobile Safari/537.36"
    ),
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def get(url: str, **kwargs) -> httpx.Response:
    """Perform a GET request with shared browser headers."""
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=20) as client:
        return client.get(url, **kwargs)


# Every scraper returns a list of dicts with these keys.
# Missing optional fields should be None, not omitted.
EVENT_SCHEMA = {
    "venue": "str",           # Display name, e.g. "A-trane"
    "venue_slug": "str",      # Machine name, e.g. "atrane"
    "venue_tag": "str",       # "jazz" | "electronic" | "live" | "bar"
    "date": "str",            # ISO 8601 date "YYYY-MM-DD"
    "time": "str | None",     # "HH:MM" 24h, or None
    "title": "str",           # Artist / event title
    "description": "str | None",
    "url": "str",             # Link to event or venue programme page
    "image_url": "str | None",
    "price": "str | None",    # e.g. "15€" or "free" or None
    "scraped_at": "str",      # ISO 8601 datetime
}
