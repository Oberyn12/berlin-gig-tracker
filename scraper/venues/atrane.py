"""
A-trane — Jazz club, Charlottenburg.
Site: https://a-trane.de/programm/

Confirmed HTML structure (WordPress + EventOn plugin):
  - Events use JSON-LD blocks: <script type="application/ld+json"> with @type="Event"
  - Fields: name, startDate (ISO with offset), endDate, url, description
  - Price: regex in description HTML "35,00 €" or "EINTRITT FREI"

JSON-LD is the cleanest extraction — no brittle CSS selectors.
"""
from __future__ import annotations

import html as html_lib
import json
import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from .base import get
from .atrane_helpers import _parse_jsonld_date, _extract_price_from_text

PROGRAMME_URL = "https://a-trane.de/programm/"
BASE_URL = "https://a-trane.de"


def scrape() -> list[dict]:
    resp = get(PROGRAMME_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    scraped_at = datetime.now(timezone.utc).isoformat()
    events = []

    # Each event has a <script type="application/ld+json"> with @type="Event"
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue

        # Handle both single objects and lists
        items = data if isinstance(data, list) else [data]
        for item in items:
            if item.get("@type") != "Event":
                continue

            name = item.get("name", "").strip()
            if not name:
                continue
            # Skip closure notices
            if "GESCHLOSSEN" in name.upper() or "CLOSED" in name.upper():
                continue
            # JSON-LD name may contain HTML entities and tags — clean them
            name = html_lib.unescape(name)  # decode &amp; &lt; etc.
            name = re.sub(r"<[^>]+>", " ", name)  # strip any actual HTML tags
            name = re.sub(r"\s+", " ", name).strip()

            start = item.get("startDate", "")
            date_str, time_str = _parse_jsonld_date(start)
            if not date_str:
                continue

            # Price from description HTML
            description_html = item.get("description", "") or ""
            price = _extract_price_from_text(description_html)

            url = item.get("url", PROGRAMME_URL)

            events.append({
                "venue": "A-trane",
                "venue_slug": "atrane",
                "venue_tag": "jazz",
                "date": date_str,
                "time": time_str,
                "title": name,
                "description": None,
                "url": url,
                "image_url": None,
                "price": price,
                "scraped_at": scraped_at,
            })

    if not events:
        raise RuntimeError(
            f"A-trane: no JSON-LD Event blocks found at {PROGRAMME_URL}"
        )

    return events
