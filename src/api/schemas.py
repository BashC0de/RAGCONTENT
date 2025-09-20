from pydantic import BaseModel
from typing import List, Optional

class ContentRequest(BaseModel):
    type: str
    topic: str
    target_audience: Optional[str] = "general"
    word_count: Optional[int] = 600
    tone: Optional[str] = "professional_conversational"
    seo_keywords: Optional[List[str]] = []

class GenerationConfig(BaseModel):
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_retrieval_docs: Optional[int] = 8

class GeneratePayload(BaseModel):
    content_request: ContentRequest
    generation_config: GenerationConfig
