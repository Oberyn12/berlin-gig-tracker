"""
Neue Zukunft — Events venue, Neukölln.

STATUS: Domain for sale (August 2026).
Both neue-zukunft.de and neuezukunft.de redirect to a domain broker.
The venue may have closed or moved to a different domain / social media presence.

Action needed:
  Search "Neue Zukunft Berlin Neukölln" to find their current presence
  (Instagram, Facebook, or a new domain). Update PROGRAMME_URL below
  and implement a scraper following the bflat.py or schokoladen.py pattern.
"""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def scrape() -> list[dict]:
    log.warning(
        "Neue Zukunft: domain for sale — venue may have closed or moved. "
        "Search for their current web presence and update this scraper. "
        "Returning empty."
    )
    return []
