"""
formatter.py
------------
Final pass to make LLM output more 'human-like' and publication-ready.

Responsibilities:
* Style/tone adjustments (casual, professional, technical, creative)
* Simple grammar cleanup & readability tweaks
* Optional HTML / Markdown formatting
* Metadata injection (source citations, generation timestamp)
"""

from typing import Dict
import datetime
import re
from src.utils.logger import logger


def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces/newlines, trim edges."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def apply_style(text: str, style: str = "professional_conversational") -> str:
    """
    Lightweight style switcher.
    For heavy rewriting, call an LLM here with a style-transfer prompt.
    """
    if style == "casual":
        # Ex: add mild contractions
        text = text.replace("do not", "don't").replace("cannot", "can't")
    elif style == "technical":
        # Could enforce shorter sentences, passive voice reduction
        # Placeholder – real logic might use spaCy or LanguageTool
        pass
    elif style == "creative":
        # Maybe add a creative sign-off or metaphorical phrases
        pass
    return text


def to_markdown(text: str, title: str = None) -> str:
    """Convert to basic Markdown with optional title."""
    md = ""
    if title:
        md += f"# {title}\n\n"
    md += text
    return md


def format_output(
    generated: Dict,
    style: str = "professional_conversational",
    output_format: str = "markdown",
    add_metadata: bool = True,
) -> Dict:
    """
    Main entry point.

    Args:
        generated: {
            "generated_text": "...",
            "model": "...",
            "metadata": { "used_docs": [...] }
        }
    Returns:
        dict with formatted_text and optional metadata
    """
    logger.info("Formatting generated content…")

    text = normalize_whitespace(generated.get("generated_text", ""))

    # Apply style adjustments
    text = apply_style(text, style)

    # Format (Markdown/HTML/Plain)
    if output_format == "markdown":
        text = to_markdown(text, title=generated.get("metadata", {}).get("title"))
    elif output_format == "html":
        text = f"<html><body><p>{text}</p></body></html>"

    result = {"formatted_text": text}

    if add_metadata:
        result["metadata"] = {
            "model": generated.get("model"),
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "sources": generated.get("metadata", {}).get("used_docs", []),
            "style_applied": style,
            "format": output_format,
        }

    return result
