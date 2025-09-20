SYSTEM_PROMPT = """
You are an elite content-generation system tasked with producing publication-ready material.
You must:
• Write with the specified style: {style}
• Maintain the requested tone: {tone}
• Target the specified audience: {audience}
• Use ONLY the supplied context for factual claims. Never fabricate or speculate.
• Cite or reference the provided context sources inline (e.g., [Source 1]) whenever you state a fact.
• If critical information is missing, explicitly say so rather than guessing.
• Prioritize clarity, logical flow, and SEO best practices.
"""

USER_PROMPT_TEMPLATE = """
Objective:
Create a {type} focused on "{topic}" of roughly {word_count} words,
optimized for {target_audience}.

Available Context:
{context}

Detailed Instructions:
• Tone & Voice: {tone}
• Style Guide: {style} (adopt consistent formatting, headings, bullet points as needed)
• SEO Keywords/Phrases: {keywords} — weave these in naturally without keyword stuffing.
• Structure: Start with a compelling hook/intro, develop key arguments or insights in well-labeled sections, and end with a concise conclusion or call to action.
• Citations: Reference context sources explicitly (e.g., “[Source 2]”) for every factual statement.
• Integrity: If the context does not supply enough evidence for a claim, clearly state that the data is unavailable.
• Output must be clean, professional, and ready for immediate publication.
"""

def build_prompt(content_request, context_docs):
    context_text = "\n\n".join(doc["text"] for doc in context_docs)
    return SYSTEM_PROMPT.format(
        style=content_request.get("style", "informative"),
        tone=content_request.get("tone", "neutral"),
        audience=content_request.get("target_audience", "general")
    ) + USER_PROMPT_TEMPLATE.format(
        type=content_request.get("type", "article"),
        topic=content_request.get("topic", "unspecified topic"),
        word_count=content_request.get("word_count", 600),
        target_audience=content_request.get("target_audience", "general audience"),
        context=context_text,
        tone=content_request.get("tone", "neutral"),
        keywords=", ".join(content_request.get("keywords", []))
    )