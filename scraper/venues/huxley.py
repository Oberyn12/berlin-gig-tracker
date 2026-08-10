"""
Huxley Neue Welt — Large concert venue, Neukölln.
Site: https://huxleysneuewelt.de/events

HTML structure (WordPress + Events Manager plugin):
  Container: div.em-list.em-events-list-grouped
  Children (siblings):
    - div.month > h3   "August 2026"
    - ul > li.event-item
      - a[href]                 → event URL (wraps the whole card)
      - div.date                → day number as text node; span = month abbrev
      - div.details > div.time  "Beginn: 20:00 | Einlass: 19:00"
      - div.details > span.eventname
  Sold-out / cancelled: extra class on li, e.g. li.event-item.Ausverkauft
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup, NavigableString, Tag
from .base import get

EVENTS_URL = "https://huxleysneuewelt.de/events"

_MONTHS_DE_EN = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "mai": 5, "may": 5,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9, "okt": 10, "oct": 10,
    "nov": 11, "dez": 12, "dec": 12,
    "januar": 1, "februar": 2, "märz": 3, "april": 4, "juni": 6,
    "juli": 7, "august": 8, "september": 9, "oktober": 10,
    "november": 11, "dezember": 12,
}


def _parse_month_header(text: str) -> tuple[int, int] | None:
    """Parse 'August 2026' → (8, 2026)."""
    m = re.match(r"(\w+)\s+(\d{4})", text.strip())
    if not m:
        return None
    month = _MONTHS_DE_EN.get(m.group(1).lower())
    if not month:
        return None
    return month, int(m.group(2))


def _parse_time(text: str) -> str | None:
    m = re.search(r"Beginn[:\s]+(\d{1,2}):(\d{2})", text, re.IGNORECASE)
    if m:
        return f"{m.group(1).zfill(2)}:{m.group(2)}"
    return None


def _day_from_date_el(el: Tag) -> str | None:
    """Extract the day number from <div class="date">18<span>Aug.</span></div>."""
    # Get direct text nodes only (ignore child span)
    for child in el.children:
        if isinstance(child, NavigableString):
            day = child.strip()
            if day.isdigit():
                return day
    # Fallback: strip span text from full text
    full = el.get_text(strip=True)
    day_only = re.sub(r"[A-Za-z.]+", "", full).strip()
    return day_only if day_only.isdigit() else None


def scrape() -> list[dict]:
    resp = get(EVENTS_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    scraped_at = datetime.now(timezone.utc).isoformat()

    container = soup.select_one("div.em-events-list-grouped")
    if not container:
        raise RuntimeError(f"Huxley: event list container not found at {EVENTS_URL}")

    events = []
    current_month, current_year = None, None

    # Top-level children: div.month and ul elements alternate
    for el in container.children:
        if not isinstance(el, Tag):
            continue

        classes = el.get("class") or []
        classes_str = " ".join(classes).lower()

        # Month header
        if "month" in classes_str and el.name == "div":
            h3 = el.find("h3")
            if h3:
                parsed = _parse_month_header(h3.get_text(strip=True))
                if parsed:
                    current_month, current_year = parsed
            continue

        # Group of events for the current month
        if el.name == "ul" and current_month:
            for li in el.find_all("li", class_="event-item"):
                li_classes = " ".join(li.get("class") or []).lower()

                # Skip sold-out and cancelled
                if any(s in li_classes for s in ("ausverkauft", "cancelled", "abgesagt")):
                    continue

                # Title
                title_el = li.select_one("span.eventname")
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                if not title:
                    continue

                # Day
                date_el = li.select_one("div.date")
                if not date_el:
                    continue
                day = _day_from_date_el(date_el)
                if not day:
                    continue

                date_str = (
                    f"{current_year}-"
                    f"{str(current_month).zfill(2)}-"
                    f"{str(day).zfill(2)}"
                )

                # Time
                time_el = li.select_one("div.time")
                time_str = _parse_time(time_el.get_text()) if time_el else None

                # URL
                link = li.select_one("a[href]")
                url = link["href"] if link else EVENTS_URL

                events.append({
                    "venue": "Huxley Neue Welt",
                    "venue_slug": "huxley",
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
        raise RuntimeError(f"Huxley: no events parsed from {EVENTS_URL}")

    return events
