"""
postprocess.py
--------------
Post-generation quality and cleanup utilities.

Responsibilities:
* Trim and normalize whitespace
* Optional grammar/style linting
* Factual accuracy checks (basic placeholder)
* Keyword & SEO checks
* Basic plagiarism / similarity scan (stub for external API)

Integrate these steps right after generator.py produces raw output.
"""

from typing import Dict, List
import re
from src.utils.logger import logger



# Core text clean-up

def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces/newlines and strip leading/trailing blanks."""
    return re.sub(r"\s+", " ", text).strip()


def remove_redundant_phrases(text: str) -> str:
    """Very light heuristic cleanup for repeated filler phrases."""
    # Ex remove double occurrences like "In conclusion, In conclusion"
    text = re.sub(r"\b(\w+(?:\s+\w+){0,3})\b\s+\1\b", r"\1", text, flags=re.IGNORECASE)
    return text


# Quality checks (placeholders for real services)

def keyword_density(text: str, keywords: List[str]) -> Dict[str, float]:
    """Return keyword density as % of total words for each keyword."""
    total_words = max(len(text.split()), 1)
    densities = {}
    lower_text = text.lower()
    for kw in keywords:
        count = lower_text.count(kw.lower())
        densities[kw] = round((count / total_words) * 100, 2)
    return densities


def basic_factual_check(text: str) -> bool:
    """
    Stub for factual accuracy. In production you might:
    * Cross-check named entities against retrieved context
    * Call a fact-checking API or secondary LLM.
    """
    logger.info("basic_factual_check: skipped (placeholder).")
    return True


def plagiarism_scan(text: str) -> float:
    """
    Placeholder for plagiarism detection.
    Return a similarity score 0–1 (1 = identical).
    Integrate a real API like Copyleaks or Turnitin here.
    """
    logger.info("plagiarism_scan: skipped (placeholder).")
    return 0.0


# Main postprocess entry point
def postprocess_generated(
    generated: Dict,
    seo_keywords: List[str] = None,
    run_factual_check: bool = False,
    run_plagiarism: bool = False,
) -> Dict:
    """
    Args:
        generated: Dict with at least {"generated_text": "..."}
        seo_keywords: optional list of keywords to measure density
        run_factual_check: run basic factual validation (placeholder)
        run_plagiarism: run plagiarism scan (placeholder)

    Returns:
        dict with cleaned_text, metrics, and original metadata
    """
    text = generated.get("generated_text", "")
    logger.info("Post-processing generated content…")

    # Cleanup
    text = normalize_whitespace(text)
    text = remove_redundant_phrases(text)

    metrics = {}
    if seo_keywords:
        metrics["keyword_density"] = keyword_density(text, seo_keywords)
    if run_factual_check:
        metrics["factual_pass"] = basic_factual_check(text)
    if run_plagiarism:
        metrics["plagiarism_score"] = plagiarism_scan(text)

    return {
        "cleaned_text": text,
        "metrics": metrics,
        "model": generated.get("model"),
        "metadata": generated.get("metadata", {}),
    }
