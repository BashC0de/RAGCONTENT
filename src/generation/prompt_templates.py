SYSTEM_PROMPT = """You are a professional content writer system. Use the provided context sources to create the required content.
Follow style: {style}, tone: {tone}, target_audience: {audience}.
Cite sources from the provided context when asserting facts.
"""
USER_PROMPT_TEMPLATE = """
Task: Write a {type} about "{topic}" of approximately {word_count} words for {target_audience}.
Context:
{context}
Instructions:
- Tone: {tone}
- SEO keywords: {keywords}
- Avoid hallucinations. If info not available in context, say so.
"""
