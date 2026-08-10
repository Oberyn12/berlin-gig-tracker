"""
Schokoladen — DIY / indie venue, Mitte.
Site: https://www.schokoladen-mitte.de/

Confirmed HTML structure (custom PHP + Bootstrap 5):
  - Event container: div.event
  - ISO date (cleanest!): div.event-info[data-event-date] → "2026-08-20"
  - Time (hidden in summary): span.d-none → "19:00 Uhr"
  - Time (in details):        div.event-facts p span → "doors 19:00 - show 20:00"
  - Category: h6.category → "Musik", "Lesung", "Film"
  - Title: h2.fw-bold
  - Subtitle: h6.subtitle
  - Ticket URL: a.ticket-btn[href] (vvk.link or tickettoaster.de)
  - Price: not shown as a number

We only scrape "Musik" category events.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from .base import get

PROGRAMME_URL = "https://www.schokoladen-mitte.de/"
BASE_URL = "https://www.schokoladen-mitte.de"


def _parse_time(text: str) -> str | None:
    """Extract concert/show time from strings like 'doors 19:00 - show 20:00'."""
    m = re.search(r"show\s+(\d{1,2}):(\d{2})", text, re.IGNORECASE)
    if m:
        return f"{m.group(1).zfill(2)}:{m.group(2)}"
    m = re.search(r"(\d{1,2}):(\d{2})\s*Uhr", text, re.IGNORECASE)
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

    for item in soup.select("div.event"):
        # Only music events
        cat_el = item.select_one("h6.category")
        if cat_el:
            cat = cat_el.get_text(strip=True)
            if cat.lower() not in {"musik", "music", "konzert", "concert", ""}:
                continue  # skip film, lesung, etc.

        # Title
        title_el = item.select_one("h2.fw-bold")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        if not title:
            continue

        # ISO date from data attribute (most reliable)
        info_el = item.select_one("div.event-info[data-event-date]")
        date_str = None
        if info_el:
            date_str = info_el.get("data-event-date", "")[:10]
        if not date_str:
            continue

        # Time — prefer detail text, fall back to hidden span
        time_str = None
        facts_el = item.select_one("div.event-facts p span")
        if facts_el:
            time_str = _parse_time(facts_el.get_text(strip=True))
        if not time_str:
            hidden_el = item.select_one("span.d-none")
            if hidden_el:
                time_str = _parse_time(hidden_el.get_text(strip=True))

        # Ticket URL
        ticket_el = item.select_one("a.ticket-btn")
        url = BASE_URL
        if ticket_el:
            href = ticket_el.get("href", "")
            url = href if href.startswith("http") else f"{BASE_URL}{href}"

        events.append({
            "venue": "Schokoladen",
            "venue_slug": "schokoladen",
            "venue_tag": "live",
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
        raise RuntimeError(f"Schokoladen: no events parsed from {PROGRAMME_URL}")

    return events
