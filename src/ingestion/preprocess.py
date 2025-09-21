import re
from typing import List

def clean_html_text(text: str) -> str:
    # Lightweight cleaning
    text = re.sub(r"\s+", " ", text).strip()
    return text

def split_to_paragraphs(text: str) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    return paragraphs
