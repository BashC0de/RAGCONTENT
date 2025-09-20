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
optimized for {target_audience} ({audience_expertise or "general"}).

Available Context:
{context}

Detailed Instructions:
• Tone & Voice: {tone or "neutral"}
• Style Guide: {style or "standard"} (adopt consistent formatting, headings, bullet points as needed)
• SEO Keywords/Phrases: {keywords or "none specified"} — weave these in naturally without keyword stuffing.
• Approx. Length: {length or "medium"} words
• Formatting: Use Markdown for headings, subheadings, bullet points, and code snippets as needed.
• Structure: Start with a compelling hook/intro, develop key arguments or insights in well-labeled sections, and end with a concise conclusion or call to action.
• Citations: Reference context sources explicitly (e.g., “[Source 2]”) for every factual statement.
• CTA: Encourage readers to comment, share, or try examples if relevant.
• Integrity: If the context does not supply enough evidence for a claim, clearly state that the data is unavailable.
• Output must be clean, professional, and ready for immediate publication.
"""

def build_prompt(content_request: dict, context_docs: list) -> str:
    """
    Build a user prompt for content generation.
    
    Args:
        content_request (dict): User request containing topic, type, tone, style, etc.
        context_docs (list): List of context documents to include in the prompt.

    Returns:
        str: Formatted prompt ready for AI generation.
    """
    # Default values for optional fields
    defaults = {
        "type": "article",
        "topic": "general",
        "tone": "neutral",
        "style": "standard",
        "target_audience": "general",
        "audience_expertise": "general",
        "length": "medium",
        "word_count": "500",
        "keywords": [],
        "additional_instructions": ""
    }

    # Merge content_request with defaults
    data = {**defaults, **content_request}

    # Combine context documents into a single string
    context_text = "\n".join([doc.get("text", "") for doc in context_docs]) if context_docs else "No context provided."

    # Prepare prompt
    prompt = f"""
Objective:
Create a {data['type']} focused on "{data['topic']}" of roughly {data['word_count']} words,
optimized for {data['target_audience']} ({data['audience_expertise']}).

Available Context:
{context_text}

Detailed Instructions:
• Tone & Voice: {data['tone']}
• Style Guide: {data['style']} (adopt consistent formatting, headings, bullet points as needed)
• SEO Keywords/Phrases: {', '.join(data['keywords']) if data['keywords'] else "none specified"} — weave these in naturally without keyword stuffing.
• Approx. Length: {data['length']} words
• Formatting: Use Markdown for headings, subheadings, bullet points, and code snippets as needed.
• Structure: Start with a compelling hook/intro, develop key arguments or insights in well-labeled sections, and end with a concise conclusion or call to action.
• Citations: Reference context sources explicitly (e.g., “[Source 2]”) for every factual statement.
• CTA: Encourage readers to comment, share, or try examples if relevant.
• Integrity: If the context does not supply enough evidence for a claim, clearly state that the data is unavailable.
• Additional Instructions: {data['additional_instructions']}
• Output must be clean, professional, and ready for immediate publication.
"""
    return prompt
