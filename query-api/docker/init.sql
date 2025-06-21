-- Enhanced PostgreSQL initialization for PGVector and LlamaIndex

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema for vector store (optional, using public by default)
-- CREATE SCHEMA IF NOT EXISTS vector_store;

-- Create table for document embeddings (LlamaIndex will create this, but we can pre-create)
CREATE TABLE IF NOT EXISTS document_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(384), -- Match embedding dimension from settings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_document_embeddings_vector 
    ON document_embeddings USING ivfflat (embedding vector_cosine_ops) 
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_document_embeddings_metadata 
    ON document_embeddings USING gin (metadata);

CREATE INDEX IF NOT EXISTS idx_document_embeddings_created_at 
    ON document_embeddings (created_at DESC);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_document_embeddings_updated_at 
    BEFORE UPDATE ON document_embeddings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON SCHEMA vector_store TO postgres;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA vector_store TO postgres;

-- Log successful initialization
SELECT 'PostgreSQL with PGVector initialized successfully' as status;