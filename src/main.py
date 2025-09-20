"""
Entry point for the RAG Content Generation Engine.
This file glues together all routers, config, logging, and startup/shutdown tasks.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.routes import router as api_router          # REST endpoints
from src.utils.logger import logger                      # Central logger
from src.config import settings                           # App config (env vars)
# Optional: preload vector DB, warm up models, etc.
from src.vector_database.store import init_vector_store 
from src.vector_database.store import add_vector, query_vector  # Example init (create if needed)
from src.tasks.celery_task import start_celery_worker     # Background tasks (if used)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup and shutdown logic for the whole app."""
    logger.info("Starting RAG Content Generation Engine…")

    # Initialize vector DB connection (Weaviate / Pinecone / etc.)
    try:
        init_vector_store()
        logger.info("Vector database initialized.")
    except Exception as e:
        logger.warning(f"Vector DB init skipped or failed: {e}")

    # Optionally kick off Celery worker or any other background services
    try:
        start_celery_worker()
        logger.info("Celery worker launched.")
    except Exception as e:
        logger.warning(f"Celery not started: {e}")

    yield  #Application runs while this context is active

    logger.info("Shutting down RAG Content Generation Engine…")
    # Add any cleanup here (close DB connections, flush caches, etc.)

app = FastAPI(
    title="RAG Content Generation Engine",
    version="1.0.0",
    lifespan=lifespan
)
from fastapi import FastAPI
from src.generation import generate_content  # or same file if you combined
from src.generation import select_model, build_prompt, retrieve_context_documents

app = FastAPI()

@app.post("/generate")
async def generate_endpoint(content_request: dict):
    # Grab documents from your RAG retriever
    context_docs = retrieve_context_documents(content_request["topic"])
    
    generation_config = {
        "model": content_request.get("model", "openai"),
        "temperature": content_request.get("temperature", 0.7),
        "max_tokens": content_request.get("max_tokens", 1500)
    }

    # 👉 THIS is where you insert those two lines
    model_choice = select_model(generation_config.get("model"))
    prompt = build_prompt(content_request, context_docs)

    result = generate_content(content_request, context_docs, generation_config)
    return result

# Register API routes
app.include_router(api_router, prefix="/api")

# Health-check endpoint 
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}

import uvicorn
from src.main import app  

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# This lets you run:  python src/main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )
