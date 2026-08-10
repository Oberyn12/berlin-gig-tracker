"""
B-Flat — Jazz and acoustic music club, Mitte.
Site: https://b-flat-berlin.de/programm/

Confirmed HTML structure (Squarespace 7.1 Summary Block):
  - Event container: div.summary-item.summary-item-record-type-event
  - Month: span.summary-thumbnail-event-date-month  → "Aug."
  - Day:   span.summary-thumbnail-event-date-day    → "11"
  - Year:  inferred (upcoming events only; use current year logic)
  - Time:  span.summary-metadata-item--tags a text  → "Doors open: 20:00 – Concert: 21:00"
  - Title: a.summary-title-link text
  - URL:   a.summary-title-link[href]  (relative → prepend base)
  - Price: not shown in listing
"""
from __future__ import annotations

import re
from datetime import datetime, date, timezone

from bs4 import BeautifulSoup
from .base import get

PROGRAMME_URL = "https://b-flat-berlin.de/programm/"
BASE_URL = "https://b-flat-berlin.de"

_MONTHS_EN_DE = {
    "jan": 1, "feb": 2, "mär": 3, "mar": 3, "apr": 4,
    "mai": 5, "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "okt": 10, "oct": 10, "nov": 11, "dez": 12, "dec": 12,
}


def _infer_year(month: int, day: int) -> int:
    today = date.today()
    try:
        candidate = date(today.year, month, day)
    except ValueError:
        return today.year
    return today.year if candidate >= today else today.year + 1


def _parse_time(text: str) -> str | None:
    """Extract HH:MM from strings like 'Doors open: 20:00 – Concert: 21:00'."""
    m = re.search(r"Concert[:\s]+(\d{1,2}):(\d{2})", text, re.IGNORECASE)
    if m:
        return f"{m.group(1).zfill(2)}:{m.group(2)}"
    m = re.search(r"(\d{1,2}):(\d{2})", text)
    if m:
        return f"{m.group(1).zfill(2)}:{m.group(2)}"
    return None


def scrape() -> list[dict]:
    resp = get(PROGRAMME_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    scraped_at = datetime.now(timezone.utc).isoformat()
    events = []

    for item in soup.select("div.summary-item.summary-item-record-type-event"):
        # Title + URL
        title_el = item.select_one("a.summary-title-link")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        if not title:
            continue
        href = title_el.get("href", "")
        url = href if href.startswith("http") else f"{BASE_URL}{href}"

        # Date
        month_el = item.select_one("span.summary-thumbnail-event-date-month")
        day_el = item.select_one("span.summary-thumbnail-event-date-day")
        if not month_el or not day_el:
            continue

        month_str = month_el.get_text(strip=True).rstrip(".").lower()[:3]
        month = _MONTHS_EN_DE.get(month_str)
        if not month:
            continue

        try:
            day = int(day_el.get_text(strip=True))
        except ValueError:
            continue

        year = _infer_year(month, day)
        date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"

        # Time
        time_str = None
        tag_el = item.select_one("span.summary-metadata-item--tags a")
        if tag_el:
            time_str = _parse_time(tag_el.get_text(strip=True))

        events.append({
            "venue": "B-Flat",
            "venue_slug": "bflat",
            "venue_tag": "jazz",
            "date": date_str,
            "time": time_str,
            "title": title,
            "description": None,
            "url": url,
            "image_url": None,
            "price": None,
            "scraped_at": scraped_at,
        })

    if not events:
        raise RuntimeError(f"B-Flat: no events parsed from {PROGRAMME_URL}")

    return events
