# RAG-Powered Content Generation Engine

An end-to-end Retrieval-Augmented Generation (RAG) system that
ingests data, stores semantic embeddings, and generates
high-quality, human-like content on demand.

## Features
- **Multi-Stage Retrieval**: Pinecone/Weaviate vector DB with hybrid embeddings
- **LLM Support**: Claude Sonnet 4 (primary), Gemini 2.5 Pro, GPT-4 Turbo fallback
- **Content Pipeline**: semantic chunking, metadata preservation,
  context-aware retrieval, and post-processing
- **MCP (Model Context Protocol) Ready**: exposes retrieval and generation
  as MCP tools (or FastAPI endpoints) so LLM clients can query directly
- **Caching & Queues**: Redis + Celery for async processing
- **Quality Assurance**: plagiarism check hooks, SEO keyword metrics,
  style/tone control

## Tech Stack
- **Backend**: FastAPI, Python 3.11
- **Orchestration**: LangChain / LlamaIndex
- **Vector Store**: Pinecone or Weaviate
- **Embeddings**: OpenAI `text-embedding-3-large` or Cohere v3
- **Queue & Cache**: Redis, Celery
- **Monitoring**: Grafana, Sentry (optional)

## Folder Layout
# RAGCONTENT
