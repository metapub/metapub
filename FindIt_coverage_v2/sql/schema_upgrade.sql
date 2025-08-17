-- FindIt Coverage Database Schema Upgrades
-- Enhanced data tracking for OA analysis and failure categorization

-- Add enhanced tracking columns to pmid_results
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS failure_reason_detailed VARCHAR(200);
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS has_alternative_ids BOOLEAN DEFAULT FALSE;
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS repository_detected VARCHAR(100);
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS publication_year INTEGER;

-- OA and access type tracking
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS oa_type VARCHAR(50);  -- 'green', 'gold', 'hybrid', 'closed', 'unknown'
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS repository_type VARCHAR(100);  -- 'PMC', 'institutional', 'preprint', 'publisher', etc.

-- Alternative identifier tracking
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS has_pmc BOOLEAN DEFAULT FALSE;
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS has_arxiv_id BOOLEAN DEFAULT FALSE;
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS other_identifiers JSONB;

-- Journal and publisher coverage analysis
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS journal_in_findit_registry BOOLEAN;
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS publisher_supported BOOLEAN;

-- Enhanced metadata for analysis
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS article_type VARCHAR(100);  -- 'research', 'review', 'editorial', etc.
ALTER TABLE pmid_results ADD COLUMN IF NOT EXISTS is_retracted BOOLEAN DEFAULT FALSE;

-- Create indexes for performance on new columns
CREATE INDEX IF NOT EXISTS idx_pmid_results_oa_type ON pmid_results(oa_type);
CREATE INDEX IF NOT EXISTS idx_pmid_results_repository_type ON pmid_results(repository_type);
CREATE INDEX IF NOT EXISTS idx_pmid_results_publication_year ON pmid_results(publication_year);
CREATE INDEX IF NOT EXISTS idx_pmid_results_has_alternative_ids ON pmid_results(has_alternative_ids);
CREATE INDEX IF NOT EXISTS idx_pmid_results_failure_reason_detailed ON pmid_results(failure_reason_detailed);

-- Enhanced views for analysis

-- DOI coverage analysis view
CREATE OR REPLACE VIEW doi_coverage_analysis AS
SELECT 
    CASE WHEN doi IS NULL OR doi = '' THEN 'No DOI' ELSE 'Has DOI' END as doi_status,
    COUNT(*) as total_pmids,
    COUNT(CASE WHEN pass1_status = 'success' THEN 1 END) as pass1_success,
    COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) as pdf_found,
    COUNT(CASE WHEN verified = TRUE THEN 1 END) as verified,
    ROUND(
        COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN pass1_status = 'success' THEN 1 END), 0), 2
    ) as pdf_success_rate,
    ROUND(
        COUNT(CASE WHEN verified = TRUE THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END), 0), 2
    ) as verification_rate
FROM pmid_results 
GROUP BY (doi IS NULL OR doi = '');

-- Open Access analysis view
CREATE OR REPLACE VIEW oa_access_analysis AS
SELECT 
    oa_type,
    repository_type,
    COUNT(*) as total_articles,
    COUNT(CASE WHEN verified = TRUE THEN 1 END) as verified_articles,
    ROUND(AVG(time_to_pdf), 3) as avg_download_time,
    ROUND(AVG(file_size::numeric / 1024 / 1024), 2) as avg_file_size_mb
FROM pmid_results 
WHERE oa_type IS NOT NULL
GROUP BY oa_type, repository_type
ORDER BY total_articles DESC;

-- Failure analysis view
CREATE OR REPLACE VIEW failure_analysis AS
SELECT 
    failure_reason_detailed,
    COUNT(*) as failure_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as failure_percentage,
    COUNT(CASE WHEN doi IS NULL OR doi = '' THEN 1 END) as failures_without_doi,
    ROUND(
        COUNT(CASE WHEN doi IS NULL OR doi = '' THEN 1 END) * 100.0 / COUNT(*), 2
    ) as pct_failures_without_doi
FROM pmid_results 
WHERE pass2_status IN ('no_pdf_url', 'no_pdf_link', 'findit_error')
AND failure_reason_detailed IS NOT NULL
GROUP BY failure_reason_detailed
ORDER BY failure_count DESC;

-- Journal coverage analysis view
CREATE OR REPLACE VIEW journal_coverage_analysis AS
SELECT 
    journal_name,
    publisher,
    journal_in_findit_registry,
    publisher_supported,
    COUNT(*) as total_articles,
    COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) as pdf_found,
    COUNT(CASE WHEN verified = TRUE THEN 1 END) as verified,
    ROUND(
        COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) * 100.0 / COUNT(*), 2
    ) as pdf_success_rate
FROM pmid_results 
WHERE journal_name IS NOT NULL
AND pass1_status = 'success'
GROUP BY journal_name, publisher, journal_in_findit_registry, publisher_supported
HAVING COUNT(*) >= 3  -- Only journals with 3+ articles
ORDER BY total_articles DESC;

-- Alternative identifiers analysis view
CREATE OR REPLACE VIEW alternative_ids_analysis AS
SELECT 
    has_pmc,
    has_arxiv_id,
    has_alternative_ids,
    CASE WHEN doi IS NULL OR doi = '' THEN 'No DOI' ELSE 'Has DOI' END as doi_status,
    COUNT(*) as total_articles,
    COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) as pdf_found,
    ROUND(
        COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) * 100.0 / COUNT(*), 2
    ) as success_rate
FROM pmid_results 
WHERE pass1_status = 'success'
GROUP BY has_pmc, has_arxiv_id, has_alternative_ids, (doi IS NULL OR doi = '')
ORDER BY total_articles DESC;

-- Publication year trends view
CREATE OR REPLACE VIEW yearly_trends_analysis AS
SELECT 
    publication_year,
    COUNT(*) as total_articles,
    COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) as pdf_found,
    COUNT(CASE WHEN verified = TRUE THEN 1 END) as verified,
    COUNT(CASE WHEN oa_type = 'green' THEN 1 END) as green_oa,
    COUNT(CASE WHEN oa_type = 'gold' THEN 1 END) as gold_oa,
    ROUND(
        COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) * 100.0 / COUNT(*), 2
    ) as pdf_success_rate,
    ROUND(
        COUNT(CASE WHEN oa_type IN ('green', 'gold') THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN verified = TRUE THEN 1 END), 0), 2
    ) as oa_percentage
FROM pmid_results 
WHERE publication_year IS NOT NULL 
AND pass1_status = 'success'
GROUP BY publication_year
ORDER BY publication_year DESC;