"""
Shared date/price parsing helpers for A-trane and B-Flat scrapers.
Split into a helper module to avoid circular imports.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone


def _parse_jsonld_date(date_str: str) -> tuple[str | None, str | None]:
    """
    Parse JSON-LD startDate like "2026-8-18T20:30+2:00" or "2026-08-18T20:30:00+02:00".
    Returns (YYYY-MM-DD, HH:MM) or (None, None).
    """
    if not date_str:
        return None, None

    # Normalise the date string — JSON-LD may use single-digit months
    m = re.match(
        r"(\d{4})-(\d{1,2})-(\d{1,2})(?:[T ](\d{1,2}):(\d{2}))?",
        date_str,
    )
    if not m:
        return None, None

    year, month, day = m.group(1), m.group(2).zfill(2), m.group(3).zfill(2)
    date_out = f"{year}-{month}-{day}"

    time_out = None
    if m.group(4) and m.group(5):
        time_out = f"{m.group(4).zfill(2)}:{m.group(5)}"

    return date_out, time_out


def _extract_price_from_text(text: str) -> str | None:
    """Extract price from HTML/text like '35,00 €' or 'EINTRITT FREI'."""
    if not text:
        return None
    # "35,00 €" or "35 €" or "€35"
    m = re.search(r"(\d+)[,.]?\d*\s*€|€\s*(\d+)", text)
    if m:
        amount = m.group(1) or m.group(2)
        return f"€{amount}"
    if re.search(r"EINTRITT FREI|eintritt frei|kostenlos|free", text, re.IGNORECASE):
        return "Free"
    return None


def _parse_german_date(text: str) -> str | None:
    """Return YYYY-MM-DD from a German date string, or None."""
    if not text:
        return None

    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})", text)
    if m:
        day, month, year = m.groups()
        year = f"20{year}" if len(year) == 2 else year
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    _MONTHS_DE = {
        "jan": 1, "feb": 2, "mär": 3, "mar": 3, "apr": 4,
        "mai": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "okt": 10, "oct": 10, "nov": 11, "dez": 12, "dec": 12,
    }
    m = re.search(r"(\d{1,2})\.?\s+([A-Za-zÄÖÜäöü]+)\s+(\d{4})", text)
    if m:
        day, month_str, year = m.groups()
        month = _MONTHS_DE.get(month_str[:3].lower())
        if month:
            return f"{year}-{str(month).zfill(2)}-{day.zfill(2)}"

    return None


def _extract_time(text: str) -> str | None:
    m = re.search(r"(\d{1,2})[:\.](\d{2})\s*(Uhr|h)?", text)
    if m:
        return f"{m.group(1).zfill(2)}:{m.group(2)}"
    return None
