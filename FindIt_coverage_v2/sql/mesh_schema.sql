-- MeSH (Medical Subject Headings) schema addition
-- Add MeSH tracking to the existing enhanced system

-- MeSH terms table
CREATE TABLE IF NOT EXISTS mesh_terms (
    id SERIAL PRIMARY KEY,
    pmid VARCHAR(20) REFERENCES pmid_results(pmid) ON DELETE CASCADE,
    mesh_id VARCHAR(20) NOT NULL,  -- MeSH descriptor ID like 'D004989'
    mesh_term VARCHAR(500) NOT NULL,  -- Descriptor name like 'Ethics'
    is_major_topic BOOLEAN DEFAULT FALSE,  -- * in PubMed (major topic)
    qualifier VARCHAR(200),  -- subheadings like "therapy", "diagnosis", NULL for base term
    qualifier_major_topic BOOLEAN DEFAULT FALSE,  -- whether the qualifier is major
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint to prevent duplicates
    UNIQUE (pmid, mesh_id, qualifier)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_mesh_terms_mesh_term ON mesh_terms(mesh_term);
CREATE INDEX IF NOT EXISTS idx_mesh_terms_major_topic ON mesh_terms(is_major_topic);
CREATE INDEX IF NOT EXISTS idx_mesh_terms_qualifier ON mesh_terms(qualifier);
CREATE INDEX IF NOT EXISTS idx_mesh_terms_mesh_id ON mesh_terms(mesh_id);

-- Add mesh summary fields to pmid_results for quick analysis
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS has_mesh_terms BOOLEAN DEFAULT FALSE;
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS mesh_term_count INTEGER DEFAULT 0;
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS major_mesh_count INTEGER DEFAULT 0;

-- View for MeSH analysis
CREATE OR REPLACE VIEW mesh_topic_analysis AS
SELECT 
    mt.mesh_term,
    mt.qualifier,
    COUNT(DISTINCT mt.pmid) as article_count,
    COUNT(CASE WHEN mt.is_major_topic THEN 1 END) as major_topic_count,
    COUNT(CASE WHEN pr.oa_type = 'green' THEN 1 END) as green_oa_count,
    COUNT(CASE WHEN pr.oa_type = 'gold' THEN 1 END) as gold_oa_count,
    COUNT(CASE WHEN pr.verified = TRUE THEN 1 END) as verified_count,
    ROUND(
        COUNT(CASE WHEN pr.oa_type IN ('green', 'gold') THEN 1 END) * 100.0 / COUNT(*), 2
    ) as oa_percentage,
    ROUND(
        COUNT(CASE WHEN pr.verified = TRUE THEN 1 END) * 100.0 / COUNT(*), 2
    ) as verification_rate
FROM mesh_terms mt
JOIN pmid_results pr ON mt.pmid = pr.pmid
WHERE pr.pass1_status = 'success'
GROUP BY mt.mesh_term, mt.qualifier
HAVING COUNT(DISTINCT mt.pmid) >= 3  -- Only terms with 3+ articles
ORDER BY article_count DESC;

-- View for major MeSH topics (most important for analysis)
CREATE OR REPLACE VIEW major_mesh_topics AS
SELECT 
    mt.mesh_term,
    COUNT(DISTINCT mt.pmid) as article_count,
    COUNT(CASE WHEN pr.oa_type = 'green' THEN 1 END) as green_oa_count,
    COUNT(CASE WHEN pr.oa_type = 'gold' THEN 1 END) as gold_oa_count,
    COUNT(CASE WHEN pr.verified = TRUE THEN 1 END) as verified_count,
    ROUND(AVG(pr.publication_year), 0) as avg_publication_year,
    ROUND(
        COUNT(CASE WHEN pr.oa_type IN ('green', 'gold') THEN 1 END) * 100.0 / COUNT(*), 2
    ) as oa_percentage
FROM mesh_terms mt
JOIN pmid_results pr ON mt.pmid = pr.pmid
WHERE mt.is_major_topic = TRUE
AND pr.pass1_status = 'success'
GROUP BY mt.mesh_term
HAVING COUNT(DISTINCT mt.pmid) >= 5  -- Only major topics with 5+ articles
ORDER BY article_count DESC;

-- View for MeSH qualifier analysis (subheadings) - simplified
CREATE OR REPLACE VIEW mesh_qualifier_analysis AS
SELECT 
    mt.qualifier,
    COUNT(DISTINCT mt.pmid) as article_count,
    COUNT(CASE WHEN pr.oa_type IN ('green', 'gold') THEN 1 END) as oa_count,
    ROUND(
        COUNT(CASE WHEN pr.oa_type IN ('green', 'gold') THEN 1 END) * 100.0 / COUNT(*), 2
    ) as oa_percentage
FROM mesh_terms mt
JOIN pmid_results pr ON mt.pmid = pr.pmid
WHERE mt.qualifier IS NOT NULL
AND pr.pass1_status = 'success'
GROUP BY mt.qualifier
HAVING COUNT(DISTINCT mt.pmid) >= 3
ORDER BY article_count DESC;