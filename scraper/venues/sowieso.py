"""
Sowieso — Improvised and experimental music, Neukölln.
Site: https://www.sowiesoberlin.com/

Data is embedded as a JSON blob in a <script type="text/json" data-set="ProjectDetail">
tag. The "content" key is a raw HTML string listing events like:

  "Jul 24&nbsp; <b>Windisch–Jermyn–Buck</b>&nbsp; Julius Windisch...<br>"

All events share:
  - Time: Doors 20:00 | Concert 20:30
  - Price: Entry by donation
  - No individual event URLs
"""
from __future__ import annotations

import json
import re
from datetime import datetime, date, timezone

from bs4 import BeautifulSoup
from .base import get

PROGRAMME_URL = "https://www.sowiesoberlin.com/"
FIXED_TIME = "20:30"   # Concert time (doors 20:00)
FIXED_PRICE = "Donation"

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    "june": 6, "july": 7, "august": 8, "january": 1, "february": 2,
    "march": 3, "april": 4, "october": 10, "november": 11, "december": 12,
    "september": 9,
}


def _infer_year(month: int, day: int) -> int:
    today = date.today()
    try:
        candidate = date(today.year, month, day)
    except ValueError:
        return today.year
    return today.year if candidate >= today else today.year + 1


def _parse_event_line(line: str, scraped_at: str) -> dict | None:
    """Parse one line like 'Jul 24  <b>Artist</b>  description'."""
    # Extract month + day
    m = re.match(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|June|July|August|"
        r"January|February|March|April|October|November|December|September)"
        r"[.\s]+(\d{1,2})",
        line.strip(),
        re.IGNORECASE,
    )
    if not m:
        return None

    month_str, day_str = m.group(1).lower(), m.group(2)
    month = _MONTHS.get(month_str[:3])
    if not month:
        return None
    day = int(day_str)
    year = _infer_year(month, day)
    date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"

    today = date.today().isoformat()
    if date_str < today:
        return None  # skip past events

    # Extract artist from <b> tag
    b_match = re.search(r"<b>(.*?)</b>", line)
    if not b_match:
        return None
    title = b_match.group(1).strip()
    if not title:
        return None

    # Description: text after </b>
    desc_match = re.search(r"</b>\s*&nbsp;\s*(.*?)$", line)
    description = None
    if desc_match:
        raw = desc_match.group(1).strip()
        description = BeautifulSoup(raw, "lxml").get_text(strip=True) or None

    return {
        "venue": "Sowieso",
        "venue_slug": "sowieso",
        "venue_tag": "jazz",
        "date": date_str,
        "time": FIXED_TIME,
        "title": title,
        "description": description,
        "url": PROGRAMME_URL,
        "image_url": None,
        "price": FIXED_PRICE,
        "scraped_at": scraped_at,
    }


def scrape() -> list[dict]:
    resp = get(PROGRAMME_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    scraped_at = datetime.now(timezone.utc).isoformat()

    # Find the JSON blob with all events
    script = soup.find("script", {"type": "text/json", "data-set": "ProjectDetail"})
    if not script or not script.string:
        raise RuntimeError("Sowieso: JSON data block not found in page")

    try:
        data = json.loads(script.string)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Sowieso: failed to parse JSON data: {e}")

    content_html = data.get("content", "")
    if not content_html:
        raise RuntimeError("Sowieso: 'content' key empty in JSON data")

    # Split into lines on <br> tags, parse each
    lines = re.split(r"<br\s*/?>", content_html)
    events = []
    for line in lines:
        ev = _parse_event_line(line, scraped_at)
        if ev:
            events.append(ev)

    if not events:
        raise RuntimeError("Sowieso: no upcoming events parsed from content")

    return events
