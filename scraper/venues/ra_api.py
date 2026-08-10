"""
Resident Advisor GraphQL helper (confirmed working endpoint).

RA GraphQL: POST https://ra.co/graphql
- Requires Content-Type: application/json and Referer: https://ra.co/
- Supports both venue ID and slug queries

RA venue IDs / slugs for our venues:
  Gretchen:           id=151604  slug=gretchen-berlin
  Festsaal Kreuzberg: id=21631   slug=festsaal-kreuzberg
  Huxley Neue Welt:   id=55665   slug=huxleys-neue-welt-berlin  (verify)
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import httpx

RA_GRAPHQL = "https://ra.co/graphql"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Referer": "https://ra.co/",
    "Origin": "https://ra.co",
}

# Query by numeric venue ID
_QUERY_BY_ID = """
query VenueEvents($id: ID!, $from: String!, $to: String!) {
  venue(id: $id) {
    name
    eventListings(filters: { from: $from, to: $to, includePast: false }) {
      data {
        listingDate
        event {
          id
          title
          startTime
          contentUrl
          images { filename }
          pick { blurb }
          tickets { price }
        }
      }
    }
  }
}
"""


def fetch_venue_events(
    venue_id: str,
    venue_name: str,
    venue_slug: str,
    venue_tag: str,
    days_ahead: int = 30,
) -> list[dict]:
    """Fetch upcoming events for a given RA venue ID via GraphQL."""
    now = datetime.now(timezone.utc)
    from_date = now.strftime("%Y-%m-%d")
    to_date = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    payload = {
        "query": _QUERY_BY_ID,
        "variables": {
            "id": venue_id,
            "from": from_date,
            "to": to_date,
        },
    }

    with httpx.Client(headers=HEADERS, timeout=20, follow_redirects=True) as client:
        resp = client.post(RA_GRAPHQL, json=payload)
        resp.raise_for_status()
        data = resp.json()

    errors = data.get("errors")
    if errors:
        raise ValueError(f"RA GraphQL errors for {venue_name}: {errors}")

    venue_data = (data.get("data") or {}).get("venue")
    if not venue_data:
        raise ValueError(f"RA: no venue found for id={venue_id} ({venue_name})")

    listings = (venue_data.get("eventListings") or {}).get("data") or []
    scraped_at = now.isoformat()
    events = []

    for listing in listings:
        ev = listing.get("event") or {}
        if not ev:
            continue

        date_str = listing.get("listingDate", "")[:10]  # "YYYY-MM-DD"

        # Convert startTime (ISO) to Berlin local time
        time_str = None
        start_time = ev.get("startTime", "")
        if start_time:
            try:
                dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                berlin = dt + timedelta(hours=2)  # CET+1 DST approximation
                time_str = berlin.strftime("%H:%M")
            except ValueError:
                pass

        # Price — cheapest available
        tickets = ev.get("tickets") or []
        price = None
        prices = [t.get("price") for t in tickets if t and t.get("price")]
        if prices:
            price = f"€{min(prices):.0f}"

        # Image
        images = ev.get("images") or []
        image_url = None
        if images and images[0].get("filename"):
            image_url = f"https://static.ra.co/images/{images[0]['filename']}"

        content_url = ev.get("contentUrl", "")
        events.append({
            "venue": venue_name,
            "venue_slug": venue_slug,
            "venue_tag": venue_tag,
            "date": date_str,
            "time": time_str,
            "title": ev.get("title", ""),
            "description": (ev.get("pick") or {}).get("blurb"),
            "url": f"https://ra.co{content_url}" if content_url else "https://ra.co/berlin",
            "image_url": image_url,
            "price": price,
            "scraped_at": scraped_at,
        })

    return events
