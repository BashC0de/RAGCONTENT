"""
filters.py
----------
Utility functions for filtering and ranking retrieved documents
before they are passed to the generation step.

Typical uses:
* Remove docs below a similarity score threshold
* Restrict to a specific content_type (blog, research_paper, etc.)
* Filter by date range or custom metadata keys
"""

from datetime import datetime
from typing import List, Dict, Optional


def by_score(
    docs: List[Dict],
    min_score: float = 0.8,
    score_key: str = "score"
) -> List[Dict]:
    """
    Keep only docs whose similarity score meets or exceeds min_score.
    If your vector DB returns distance instead of similarity, invert logic.
    """
    filtered = [d for d in docs if d.get(score_key, 0) >= min_score]
    return filtered


def by_content_type(
    docs: List[Dict],
    allowed_types: Optional[List[str]] = None
) -> List[Dict]:
    """
    Filter documents by metadata['content_type'].
    allowed_types example: ["research_paper", "industry_report"]
    """
    if not allowed_types:
        return docs
    return [
        d for d in docs
        if d.get("metadata", {}).get("content_type") in allowed_types
    ]


def by_date_range(
    docs: List[Dict],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    date_key: str = "last_updated"
) -> List[Dict]:
    """
    Filter documents based on a metadata timestamp.
    Metadata should store an ISO8601 string or datetime object.
    """
    if not (start or end):
        return docs

    def in_range(d):
        raw = d.get("metadata", {}).get(date_key)
        if not raw:
            return False
        if isinstance(raw, str):
            try:
                ts = datetime.fromisoformat(raw)
            except ValueError:
                return False
        else:
            ts = raw
        if start and ts < start:
            return False
        if end and ts > end:
            return False
        return True

    return [d for d in docs if in_range(d)]


def apply_filters(
    docs: List[Dict],
    min_score: float = 0.8,
    allowed_types: Optional[List[str]] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None
) -> List[Dict]:
    """
    Convenience wrapper to apply multiple filters in one call.
    """
    filtered = by_score(docs, min_score=min_score)
    filtered = by_content_type(filtered, allowed_types)
    filtered = by_date_range(filtered, start, end)
    return filtered
