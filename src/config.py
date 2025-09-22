import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", 8000))

    PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "claude-sonnet-4")
    SECONDARY_MODEL = os.getenv("SECONDARY_MODEL", "gemini-2.5-pro")
    FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gpt-4o")

    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV = os.getenv("PINECONE_ENV")

    WEAVIATE_URL = os.getenv("WEAVIATE_URL")
    WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
settings = Settings()

#removed the things and cleaned up imports