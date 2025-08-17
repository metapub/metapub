-- FindIt Coverage Testing Database Schema
-- PostgreSQL database for tracking PMID processing across multiple passes

-- Main table for tracking PMID processing results
CREATE TABLE IF NOT EXISTS pmid_results (
    -- Primary identifier
    pmid VARCHAR(20) PRIMARY KEY,
    
    -- Article metadata (populated in pass1)
    title TEXT,
    journal_name VARCHAR(500),
    publisher VARCHAR(200),
    doi VARCHAR(200),
    pii VARCHAR(100),
    pmc VARCHAR(20),
    
    -- FindIt results (populated in pass2)
    pdf_url TEXT,
    findit_reason VARCHAR(500),
    
    -- Verification results (populated in pass3)
    verified BOOLEAN DEFAULT FALSE,
    time_to_pdf DECIMAL(8,3), -- seconds with millisecond precision
    http_status_code INTEGER,
    content_type VARCHAR(100),
    file_size BIGINT, -- bytes
    
    -- Processing status tracking
    is_good_pmid BOOLEAN DEFAULT TRUE, -- FALSE if PMID retired/invalid
    pass1_status VARCHAR(50), -- 'success', 'not_found', 'error'
    pass2_status VARCHAR(50), -- 'pdf_url_found', 'no_pdf_url', 'error'
    pass3_status VARCHAR(50), -- 'verified', 'failed', 'error'
    
    -- Error tracking
    pass1_error TEXT,
    pass2_error TEXT,
    pass3_error TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    pass1_completed_at TIMESTAMP WITH TIME ZONE,
    pass2_completed_at TIMESTAMP WITH TIME ZONE,
    pass3_completed_at TIMESTAMP WITH TIME ZONE
);

-- Table for tracking PMID lists/datasets
CREATE TABLE IF NOT EXISTS pmid_lists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    file_path TEXT,
    total_pmids INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Junction table for PMID list membership
CREATE TABLE IF NOT EXISTS pmid_list_members (
    list_id INTEGER REFERENCES pmid_lists(id) ON DELETE CASCADE,
    pmid VARCHAR(20) REFERENCES pmid_results(pmid) ON DELETE CASCADE,
    position INTEGER, -- Order in the original list
    PRIMARY KEY (list_id, pmid)
);

-- Table for tracking processing runs/batches
CREATE TABLE IF NOT EXISTS processing_runs (
    id SERIAL PRIMARY KEY,
    list_id INTEGER REFERENCES pmid_lists(id),
    pass_type VARCHAR(10) NOT NULL, -- 'pass1', 'pass2', 'pass3'
    status VARCHAR(20) DEFAULT 'running', -- 'running', 'completed', 'failed', 'cancelled'
    start_index INTEGER DEFAULT 0,
    end_index INTEGER,
    total_processed INTEGER DEFAULT 0,
    successful INTEGER DEFAULT 0,
    failed INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_pmid_results_journal ON pmid_results(journal_name);
CREATE INDEX IF NOT EXISTS idx_pmid_results_publisher ON pmid_results(publisher);
CREATE INDEX IF NOT EXISTS idx_pmid_results_pass1_status ON pmid_results(pass1_status);
CREATE INDEX IF NOT EXISTS idx_pmid_results_pass2_status ON pmid_results(pass2_status);
CREATE INDEX IF NOT EXISTS idx_pmid_results_pass3_status ON pmid_results(pass3_status);
CREATE INDEX IF NOT EXISTS idx_pmid_results_verified ON pmid_results(verified);
CREATE INDEX IF NOT EXISTS idx_pmid_results_updated_at ON pmid_results(updated_at);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_pmid_results_updated_at 
    BEFORE UPDATE ON pmid_results 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pmid_lists_updated_at 
    BEFORE UPDATE ON pmid_lists 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE OR REPLACE VIEW pmid_summary AS
SELECT 
    COUNT(*) as total_pmids,
    COUNT(CASE WHEN pass1_status = 'success' THEN 1 END) as pass1_success,
    COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) as pdf_urls_found,
    COUNT(CASE WHEN verified = TRUE THEN 1 END) as verified_pdfs,
    ROUND(
        COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN pass1_status = 'success' THEN 1 END), 0), 2
    ) as pdf_availability_rate,
    ROUND(
        COUNT(CASE WHEN verified = TRUE THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END), 0), 2
    ) as verification_success_rate
FROM pmid_results;

-- View for publisher statistics
CREATE OR REPLACE VIEW publisher_stats AS
SELECT 
    publisher,
    COUNT(*) as total_articles,
    COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) as pdf_urls_found,
    COUNT(CASE WHEN verified = TRUE THEN 1 END) as verified_pdfs,
    ROUND(
        COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) * 100.0 / COUNT(*), 2
    ) as pdf_availability_rate,
    ROUND(
        COUNT(CASE WHEN verified = TRUE THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END), 0), 2
    ) as verification_success_rate,
    ROUND(AVG(time_to_pdf), 3) as avg_download_time
FROM pmid_results 
WHERE publisher IS NOT NULL 
GROUP BY publisher 
ORDER BY total_articles DESC;