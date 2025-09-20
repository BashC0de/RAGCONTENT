"""
Entry point for the RAG Content Generation Engine.
This file glues together all routers, config, logging, and startup/shutdown tasks.
"""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from dotenv import load_dotenv

from src.api.routes import router as api_router          # REST endpoints
from src.utils.logger import logger                      # Central logger
from src.config import settings                          # App config (env vars)
from src.vector_database.store import init_vector_store   # Vector DB init
from src.tasks.celery_task import start_celery_worker    # Background tasks
from src.generation import generate_content, select_model, build_prompt, retrieve_context_documents

# Load environment variables
load_dotenv()
print("PINECONE_API_KEY:", os.getenv("PINECONE_API_KEY"))  # verify env loaded

# App lifespan (startup/shutdown)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting RAG Content Generation Engine…")

    # Initialize vector DB connection
    try:
        init_vector_store()
        logger.info("Vector database initialized.")
    except Exception as e:
        logger.warning(f"Vector DB init skipped or failed: {e}")

    # Start Celery worker (background tasks)
    try:
        start_celery_worker()
        logger.info("Celery worker launched.")
    except Exception as e:
        logger.warning(f"Celery not started: {e}")

    yield  # App runs while this context is active

    logger.info("Shutting down RAG Content Generation Engine…")
    # Add any cleanup here (close DB connections, flush caches, etc.)


# FastAPI app

app = FastAPI(
    title="RAG Content Generation Engine",
    version="1.0.0",
    lifespan=lifespan
)

# Health-check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}

# RAG content generation endpoint
@app.post("/generate")
async def generate_endpoint(content_request: dict):
    # Retrieve documents
    context_docs = retrieve_context_documents(content_request["topic"])
    
    # Build generation config
    generation_config = {
        "model": content_request.get("model", "openai"),
        "temperature": content_request.get("temperature", 0.7),
        "max_tokens": content_request.get("max_tokens", 1500)
    }

    # Model selection & prompt building
    model_choice = select_model(generation_config.get("model"))
    prompt = build_prompt(content_request, context_docs)

    # Generate content
    result = generate_content(content_request, context_docs, generation_config)
    return result

# Include additional API routes
app.include_router(api_router, prefix="/api")


# Uvicorn entry

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )
