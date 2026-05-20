-- ========================================================
-- BriefToScope - AI Vector Memory Scaffolding (pgvector)
-- Stack: Supabase PostgreSQL + pgvector
-- Usage: Disabled by default, enabled via ENABLE_VECTOR_MEMORY=true
-- ========================================================

-- Enable the pgvector extension if it is supported / available in the DB
-- NOTE: In local Docker PostgreSQL instances, this requires installing pgvector.
-- In Supabase, this extension is pre-installed and can be enabled natively.
CREATE EXTENSION IF NOT EXISTS vector;

-- Scaffolding the AI Memory Chunks table
-- This stores text chunk embeddings from SOW sections, client feedback, 
-- or meeting transcripts to power similar clause suggestions and stylistic memory.
CREATE TABLE IF NOT EXISTS ai_memory_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    source_type VARCHAR(100) NOT NULL, -- e.g., 'sow_section', 'transcript_segment', 'clause_style'
    source_id UUID NOT NULL,            -- ID referencing the source record
    content TEXT NOT NULL,
    metadata_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    embedding vector(1536),             -- OpenAI text-embedding-3-small/ada-002 standard dimensions (1536)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Indexing for Cosine similarity search (common for text embeddings)
-- We use an HNSW index for fast approximate nearest neighbor (ANN) search.
-- HNSW is faster and more accurate than IVFFlat for most use-cases but takes more memory.
CREATE INDEX IF NOT EXISTS idx_ai_memory_chunks_embedding_cosine 
ON ai_memory_chunks USING hnsw (embedding vector_cosine_ops);

-- Indexing on standard foreign key references for metadata queries
CREATE INDEX IF NOT EXISTS idx_ai_memory_chunks_user_id ON ai_memory_chunks(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_memory_chunks_project_id ON ai_memory_chunks(project_id);
CREATE INDEX IF NOT EXISTS idx_ai_memory_chunks_source ON ai_memory_chunks(source_type, source_id);

-- Enforce Row Level Security (RLS) on vector chunks
ALTER TABLE ai_memory_chunks ENABLE ROW LEVEL SECURITY;

-- Policy: Select policy restricted to project owner
CREATE POLICY select_ai_memory_chunks ON ai_memory_chunks
    FOR SELECT
    USING (user_id = get_current_user_id());

-- Policy: Insert policy restricted to project owner
CREATE POLICY insert_ai_memory_chunks ON ai_memory_chunks
    FOR INSERT
    WITH CHECK (user_id = get_current_user_id());

-- Policy: Delete policy restricted to project owner
CREATE POLICY delete_ai_memory_chunks ON ai_memory_chunks
    FOR DELETE
    USING (user_id = get_current_user_id());
