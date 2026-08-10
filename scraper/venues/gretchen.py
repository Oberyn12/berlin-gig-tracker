"""
Gretchen — Electronic club, Neukölln.
Primary: website scraper (gretchen-club.de — SSR PHP, no class names).
Fallback: Resident Advisor GraphQL API.

HTML structure (confirmed):
  - Events are blocks anchored by <a href="detail.php?id=NNNN">
  - Date: <strong>DD.MM.YYYY</strong>
  - Time: text "Doors: HH:MM"
  - Title: <a href="detail.php?id=NNNN"> text
  - Price: <em> tag containing "Vorverkauf ab X €..."
  - Image: <img src="./bilder_upload/...">
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from .base import get
from .atrane_helpers import _parse_german_date, _extract_time, _extract_price_from_text as _extract_price

BASE_URL = "https://www.gretchen-club.de"
INDEX_URL = "https://www.gretchen-club.de/"


def _scrape_website() -> list[dict]:
    resp = get(INDEX_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    scraped_at = datetime.now(timezone.utc).isoformat()
    events = []

    # Collect unique event detail IDs to avoid duplicates from multiple anchor tags
    seen_ids: set[str] = set()
    detail_links = soup.find_all("a", href=lambda h: h and "detail.php?id=" in h)

    for link in detail_links:
        event_id = re.search(r"id=(\d+)", link["href"])
        if not event_id:
            continue
        eid = event_id.group(1)
        if eid in seen_ids:
            continue
        seen_ids.add(eid)

        # Walk up to the enclosing event block
        # The block structure is a flat sequence; we look for the nearby <strong> with a date
        # and the parent container or table cell
        block = link.find_parent("td") or link.find_parent("div") or link.parent

        # Find the clean event title: collect all anchor texts for this ID,
        # remove "[INFO]" fragments, skip "INFO" stubs, pick the cleanest one.
        all_links = soup.find_all("a", href=link["href"])
        candidates = []
        for a in all_links:
            t = a.get_text(strip=True).replace("[INFO]", "").strip()
            if t and t.upper() not in {"INFO", "TICKETS", "MEHR", "MORE"}:
                candidates.append(t)

        if not candidates:
            continue
        # Prefer the longest text (most informative)
        title = max(candidates, key=len)

        # Date: find the nearest <strong> with a date pattern in the block or its context
        block_text = block.get_text() if block else ""
        date_str = _parse_german_date(block_text)
        if not date_str:
            continue

        # Time: "Doors: HH:MM" pattern
        time_str = None
        m = re.search(r"Doors?\s*[:\s]\s*(\d{1,2})[:\.](\d{2})", block_text, re.IGNORECASE)
        if m:
            time_str = f"{m.group(1).zfill(2)}:{m.group(2)}"

        # Price: <em> tag pattern "Vorverkauf ab X €"
        price = None
        em = block.find("em") if block else None
        if em:
            em_text = em.get_text()
            m = re.search(r"Vorverkauf ab\s*(\d+)\s*€", em_text, re.IGNORECASE)
            if m:
                price = f"€{m.group(1)}"

        # Image
        img = block.find("img", src=lambda s: s and "bilder_upload" in s) if block else None
        image_url = None
        if img:
            src = img["src"]
            image_url = src if src.startswith("http") else urljoin(BASE_URL, src)

        # Event URL
        event_url = urljoin(BASE_URL, f"detail.php?id={eid}")

        events.append({
            "venue": "Gretchen",
            "venue_slug": "gretchen",
            "venue_tag": "electronic",
            "date": date_str,
            "time": time_str,
            "title": title,
            "description": None,
            "url": event_url,
            "image_url": image_url,
            "price": price,
            "scraped_at": scraped_at,
        })

    if not events:
        raise RuntimeError(
            f"Gretchen: no events parsed from {INDEX_URL} "
            "(site structure may have changed)"
        )

    return events


def scrape() -> list[dict]:
    return _scrape_website()
