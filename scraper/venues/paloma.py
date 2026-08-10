"""
Paloma Bar — Electronic/club bar, Kreuzberg.
Site: https://palomabar.de/programm.php

Confirmed HTML structure (no CSS class names, uses <b> tags):
  - Date header: <b>FREITAG 14/08 23:00</b>  (inside a black <div>)
  - Event title: second <b> tag in the block, contains <div>
  - Artists: <td class=kotti_online_td>ARTIST NAME</td>
  - No prices, no individual event URLs

Date format: "WEEKDAY DD/MM HH:MM" (no year — infer from context)
"""
from __future__ import annotations

import re
from datetime import datetime, date, timezone

from bs4 import BeautifulSoup
from .base import get

PROGRAMME_URL = "https://palomabar.de/programm.php"
BASE_URL = "https://palomabar.de"

# German weekday prefix used as event separator
_DATE_RE = re.compile(
    r"(FREITAG|SAMSTAG|SONNTAG|MONTAG|DIENSTAG|MITTWOCH|DONNERSTAG)"
    r"\s+(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})",
    re.IGNORECASE,
)


def _infer_year(day: int, month: int) -> int:
    today = date.today()
    try:
        candidate = date(today.year, month, day)
    except ValueError:
        return today.year
    if candidate < today:
        return today.year + 1
    return today.year


def scrape() -> list[dict]:
    resp = get(PROGRAMME_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    scraped_at = datetime.now(timezone.utc).isoformat()
    events = []

    # All <b> tags: date headers and event titles alternate
    b_tags = soup.find_all("b")

    # Find <b> tags whose text matches the date pattern
    i = 0
    while i < len(b_tags):
        b_text = b_tags[i].get_text(strip=True)
        m = _DATE_RE.search(b_text)
        if m:
            # Parse date + time
            _, day_s, month_s, hour_s, min_s = m.groups()
            day, month = int(day_s), int(month_s)
            year = _infer_year(day, month)
            date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
            time_str = f"{hour_s.zfill(2)}:{min_s}"

            # Next <b> tag(s): find the event title — skip empty ones
            title = ""
            j = i + 1
            while j < len(b_tags) and not title:
                candidate = b_tags[j].get_text(strip=True)
                if candidate and not _DATE_RE.search(candidate):
                    title = candidate
                j += 1

            if title:
                events.append({
                    "venue": "Paloma Bar",
                    "venue_slug": "paloma",
                    "venue_tag": "electronic",
                    "date": date_str,
                    "time": time_str,
                    "title": title,
                    "description": None,
                    "url": PROGRAMME_URL,
                    "image_url": None,
                    "price": None,
                    "scraped_at": scraped_at,
                })
        i += 1

    if not events:
        raise RuntimeError(f"Paloma Bar: no events parsed from {PROGRAMME_URL}")

    return events
