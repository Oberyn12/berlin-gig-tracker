"""
ZigZag Jazz Club — Tempelhof.

STATUS: Domain NXDOMAIN (confirmed August 2026).
The domain zigzag-berlin.de does not resolve. The venue may have:
  - Closed permanently
  - Moved to a different domain
  - Merged with another venue

Action needed: check the venue's Instagram or search "ZigZag Jazz Berlin"
to find their current web presence. Update PROGRAMME_URL once found and
implement a scraper following the pattern in bflat.py or atrane.py.
"""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def scrape() -> list[dict]:
    log.warning(
        "ZigZag: domain zigzag-berlin.de is NXDOMAIN. "
        "Search for the venue's current website and update this scraper. "
        "Returning empty."
    )
    return []
