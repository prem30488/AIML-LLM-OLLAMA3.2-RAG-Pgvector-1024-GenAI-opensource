CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS hstore;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS vector_store (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    content text,
    metadata json,
    embedding vector(1024)  -- 1536 is the default embedding dimension
);

-- 1. Create the custom ENUM type first (REQUIRED for PostgreSQL)
DROP TYPE IF EXISTS sentiment_type CASCADE;
CREATE TYPE sentiment_type AS ENUM (
    'POSITIVE',
    'NEGATIVE',
    'NEUTRAL',
    'MIXED'
);

-- 2. Create the UUID extension if you haven't already (OPTIONAL, but recommended)
-- NOTE: If using PostgreSQL 13+, you can use gen_random_uuid() which doesn't require this extension.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
DROP TABLE IF EXISTS sentiment_feedback;
-- 3. Create the table
CREATE TABLE IF NOT EXISTS sentiment_feedback (
    id 				BIGSERIAL PRIMARY KEY,
	content 		text 		NOT NULL,
	sentiment_score real 		NOT NULL CHECK (sentiment_score BETWEEN -1.0 AND 1.0),
	created_at 		TIMESTAMPTZ DEFAULT NOW() NOT NULL, 
	sentiment text NOT NULL
);

CREATE INDEX ON vector_store USING HNSW (embedding vector_cosine_ops);

DROP TABLE IF EXISTS web_search_documents;

CREATE TABLE IF NOT EXISTS web_search_documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(768),
    topic TEXT,
    url TEXT,
    published_at TIMESTAMP,
    sentiment FLOAT
);
