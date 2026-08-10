"""
Donau115 — Bar / events venue, Neukölln.
Site: donau115.de (JS-rendered)

Data source: PUBLIC Firebase Realtime Database REST API (no auth needed).
  GET https://shifts-a77a1-default-rtdb.europe-west1.firebasedatabase.app/events.json

JSON record structure:
  {
    "bandName": "BORT!",
    "date": "2026-04-24",            # ISO YYYY-MM-DD
    "description": "she has risen!",
    "facebook": "https://fb.com/events/...",
    "live": true,
    "images": ["http://...jpg"]
  }

No time or price available.
"""
from __future__ import annotations

from datetime import datetime, date, timezone

import httpx

FIREBASE_URL = (
    "https://shifts-a77a1-default-rtdb.europe-west1.firebasedatabase.app/events.json"
)
VENUE_URL = "https://donau115.de/"


def scrape() -> list[dict]:
    resp = httpx.get(FIREBASE_URL, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    if not isinstance(data, dict):
        raise RuntimeError(f"Donau115: unexpected Firebase response type: {type(data)}")

    today = date.today().isoformat()
    scraped_at = datetime.now(timezone.utc).isoformat()
    events = []

    for record in data.values():
        if not isinstance(record, dict):
            continue

        event_date = record.get("date", "")
        if not event_date or event_date < today:
            continue  # skip past events

        title = record.get("bandName", "").strip()
        if not title:
            continue

        # Use Facebook event URL if available, else fallback to venue page
        url = record.get("facebook") or VENUE_URL

        # Image: skip base64 (large), only use http/https URLs
        images = record.get("images") or []
        image_url = None
        for img in images:
            if isinstance(img, str) and img.startswith("http"):
                image_url = img
                break

        events.append({
            "venue": "Donau115",
            "venue_slug": "donau115",
            "venue_tag": "bar",
            "date": event_date,
            "time": None,
            "title": title,
            "description": record.get("description") or None,
            "url": url,
            "image_url": image_url,
            "price": None,
            "scraped_at": scraped_at,
        })

    if not events:
        raise RuntimeError("Donau115: no upcoming events found in Firebase")

    return events
