"""
Entry point for the RAG Content Generation Engine.
This file glues together all routers, config, logging, and startup/shutdown tasks.
"""

from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from dotenv import load_dotenv

from src.api.routes import router as api_router          # Extra REST endpoints
from src.utils.logger import logger                      # Centralized logging
from src.config import settings                          # Env/config variables
from src.vector_database.store import init_vector_store   # Vector DB init
from src.tasks.celery_task import start_celery_worker    # Background tasks
from src.generation_pipeline.generator import generate_content, select_model
from src.generation.prompt_templates import build_prompt
from src.generation.orchestrator import retrieve_context_documents
from src.human_output.formatter import format_output
from src.generation_pipeline.generator import generate_content

load_dotenv()
print("PINECONE_API_KEY:", os.getenv("PINECONE_API_KEY"))
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
print("OpenAI API Key Loaded:", bool(openai.api_key))

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting RAG Content Generation Engine…")

    try:
        init_vector_store()
        logger.info("Vector database initialized.")
    except Exception as e:
        logger.warning(f"Vector DB init skipped or failed: {e}")

    try:
        start_celery_worker()
        logger.info("Celery worker launched.")
    except Exception as e:
        logger.warning(f"Celery not started: {e}")

    yield  # app runs here

    logger.info("Shutting down RAG Content Generation Engine…")

query = "Explain how vector databases are used in RAG systems."
context_docs = retrieve_context_documents(query)  
generation_config = {
    "model": "openai",
    "temperature": 0.7,
    "max_tokens": 1500
}
content_request = {
    "query": query,                       # The main user query or topic
    "topic": query,                       # Topic for the content
    "type": "blog",                        # Content type: blog, email, social_post, etc.
    "tone": "professional",               # Tone: professional, casual, humorous, etc.
    "style": "professional_conversational", # Style: professional_conversational, technical, etc.
    "target_audience": "developers",      # Audience: developers, marketers, students, general
    "length": "medium",                    # Optional: short, medium, long
    # "style": "informative",                # Optional: narrative, informative, persuasive, etc.
    "keywords": [],                        # Optional: list of keywords to include
    "additional_instructions": ""         # Optional: any extra instructions for the model
}

# Call your content generation function
raw_output = generate_content(content_request, context_docs, generation_config)

formatted_output = format_output(
    generated=raw_output,
    style="professional_conversational",
    output_format="markdown",
    add_metadata=True
)
print(formatted_output["formatted_text"])
raw_output = generate_content(query, context_docs, generation_config)

from src.human_output.formatter import format_output
formatted_output = format_output(
    generated=raw_output,
    style="professional_conversational",
    output_format="markdown",
    add_metadata=True
)
print(formatted_output["formatted_text"])

app = FastAPI(
    title="RAG Content Generation Engine",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}

@app.post("/generate")
async def generate_endpoint(content_request: dict):
    context_docs = retrieve_context_documents(content_request["topic"])
    generation_config = {
        "model": content_request.get("model", "openai"),
        "temperature": content_request.get("temperature", 0.7),
        "max_tokens": content_request.get("max_tokens", 1500)
    }
    model_choice = select_model(generation_config.get("model"))
    prompt = build_prompt(content_request, context_docs)
    result = generate_content(content_request, context_docs, generation_config)
    return result

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )

