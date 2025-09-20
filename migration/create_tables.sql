CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE content_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_url TEXT,
    content_type VARCHAR(50),
    last_updated TIMESTAMP,
    embedding_vector BYTEA,
    metadata JSONB
);

CREATE TABLE generated_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_type VARCHAR(50),
    topic VARCHAR(200),
    generated_text TEXT,
    source_references UUID[],
    quality_scores JSONB,
    created_at TIMESTAMP DEFAULT now()
);
