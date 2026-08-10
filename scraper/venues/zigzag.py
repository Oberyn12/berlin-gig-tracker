"""
ZigZag Jazz Club — Tempelhof.
Site: https://www.zigzag-jazzclub.berlin/

Confirmed HTML structure (Squarespace — identical pattern to B-Flat):
  - Event container: div.summary-item.summary-item-record-type-event
  - Full date text: time.summary-metadata-item--date → "August 11, 2026"
  - Title: div.summary-title a.summary-title-link
  - URL:   same a[href] (relative → prepend base)
  - Genre: div.summary-excerpt (e.g. "Jazz / Funk / Groove")
  - No time or price in list view
"""
from __future__ import annotations

from datetime import datetime, timezone

from bs4 import BeautifulSoup
from .base import get

PROGRAMME_URL = "https://www.zigzag-jazzclub.berlin/"
BASE_URL = "https://www.zigzag-jazzclub.berlin"


def _parse_date(text: str) -> str | None:
    """Parse 'August 11, 2026' or 'Aug 11, 2026' → 'YYYY-MM-DD'."""
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(text.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def scrape() -> list[dict]:
    resp = get(PROGRAMME_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    scraped_at = datetime.now(timezone.utc).isoformat()
    events = []

    for item in soup.select("div.summary-item.summary-item-record-type-event"):
        # Title + URL
        link = item.select_one("div.summary-title a.summary-title-link")
        if not link:
            continue
        title = link.get_text(strip=True)
        if not title:
            continue
        href = link.get("href", "")
        url = href if href.startswith("http") else f"{BASE_URL}{href}"

        # Full date text: "August 11, 2026"
        date_el = item.select_one("time.summary-metadata-item--date")
        date_str = None
        if date_el:
            date_str = _parse_date(date_el.get_text(strip=True))
        if not date_str:
            continue

        # Genre from excerpt
        excerpt_el = item.select_one("div.summary-excerpt")
        description = excerpt_el.get_text(strip=True) if excerpt_el else None

        events.append({
            "venue": "ZigZag",
            "venue_slug": "zigzag",
            "venue_tag": "jazz",
            "date": date_str,
            "time": None,  # Not in list view
            "title": title,
            "description": description,
            "url": url,
            "image_url": None,
            "price": None,
            "scraped_at": scraped_at,
        })

    if not events:
        raise RuntimeError(f"ZigZag: no events parsed from {PROGRAMME_URL}")

    return events
