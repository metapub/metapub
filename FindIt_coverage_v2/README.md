# FindIt Coverage Testing System v2

A PostgreSQL-backed system for comprehensive testing of FindIt PDF URL discovery and verification across large PMID datasets.

## Overview

This system provides a robust framework for testing FindIt's performance at scale with proper data persistence, resume capabilities, and detailed analytics. The system is organized into three main processing passes:

1. **Pass 1**: Article metadata fetching from PubMed
2. **Pass 2**: PDF URL discovery using FindIt (unverified)
3. **Pass 3**: PDF URL verification with download testing

## Architecture

```
FindIt_coverage_v2/
├── bin/                    # Executable scripts
│   ├── database.py         # Database utilities and connection management
│   ├── pmid_manager.py     # PMID list loading and management
│   ├── pass1_article_fetching.py    # Pass 1: Article metadata fetching
│   ├── pass2_pdf_finding.py         # Pass 2: PDF URL finding
│   ├── pass3_pdf_verification.py    # Pass 3: PDF verification
│   └── reports.py          # Reporting and analytics
├── data/                   # Data storage
│   ├── downloads/          # Downloaded files (if any)
│   ├── exports/           # Exported reports and data
│   └── pmid_lists/        # PMID list files
├── log/                   # Log files
├── sql/                   # Database schema and scripts
│   └── schema.sql         # PostgreSQL database schema
└── README.md              # This file
```

## Prerequisites

1. **PostgreSQL**: Database server (version 12+)
2. **Python packages**: psycopg2, requests, metapub
3. **Environment variables** (optional):
   - `FINDIT_DB_HOST` (default: localhost)
   - `FINDIT_DB_PORT` (default: 5432)
   - `FINDIT_DB_NAME` (default: findit_coverage)
   - `FINDIT_DB_USER` (default: postgres)
   - `FINDIT_DB_PASSWORD` (default: empty)

## Setup

### 1. Database Setup

```bash
# Create database
createdb findit_coverage

# Initialize schema
cd FindIt_coverage_v2/bin
python database.py --init

# Test connection
python database.py --test
```

### 2. Load PMID Lists

```bash
# Load PMIDs from a file
python pmid_manager.py load --name "Test Set 1" --file ../data/pmid_lists/test_pmids.txt

# Load with description
python pmid_manager.py load --name "Large Sample" --file large_set.txt --description "10k random PMIDs"

# List all PMID lists
python pmid_manager.py list
```

## Usage

### Processing Pipeline

Run the three passes in sequence for any PMID list:

```bash
# Pass 1: Fetch article metadata
python pass1_article_fetching.py --list-id 1

# Pass 2: Find PDF URLs
python pass2_pdf_finding.py --list-id 1

# Pass 3: Verify PDF URLs
python pass3_pdf_verification.py --list-id 1
```

### Resume Capabilities

All scripts support resuming from interruptions:

```bash
# Auto-resume without prompting
python pass2_pdf_finding.py --list-id 1 --auto-resume

# Manual start index
python pass3_pdf_verification.py --list-id 1 --start-index 5000
```

### Subset Processing

Process specific ranges for testing or parallel processing:

```bash
# Process subset (indices 1000-2000)
python pass1_article_fetching.py --list-id 1 --start-index 1000 --end-index 2000
```

### Reporting and Analytics

```bash
# Overall summary
python reports.py summary

# Publisher performance
python reports.py publisher-stats --top 20

# Journal performance
python reports.py journal-stats --top 30

# Processing run history
python reports.py runs

# Export data
python reports.py export --list-id 1 --format csv
python reports.py export --format json --output all_results.json
```

## Database Schema

The system uses four main tables:

- **`pmid_results`**: Main table storing all PMID processing results and metrics
- **`pmid_lists`**: Metadata about PMID datasets
- **`pmid_list_members`**: Junction table linking PMIDs to lists
- **`processing_runs`**: Tracking of processing batches and runs

Key metrics tracked:
- Article metadata (title, journal, DOI, PII, PMC)
- PDF URLs and FindIt results
- Verification status and download metrics
- Processing status for each pass
- Error tracking and debugging information

## Key Features

### Robust Error Handling
- Graceful handling of network failures, timeouts, and API errors
- Detailed error logging and tracking
- Automatic retry logic for transient failures

### Performance Monitoring
- Download time measurement
- File size tracking
- HTTP status code monitoring
- Content type validation

### Flexible Processing
- Process any PMID list at any time
- Resume from interruptions
- Parallel processing support (via index ranges)
- Real-time progress reporting

### Comprehensive Analytics
- Publisher and journal performance analysis
- Success rate tracking across all passes
- Export capabilities for external analysis
- Processing run history and audit trails

## Command Examples

### Complete Workflow Example

```bash
# 1. Load a PMID list
python pmid_manager.py load --name "Nature Sample" --file nature_pmids.txt

# 2. Check what lists are available
python pmid_manager.py list

# 3. Run complete processing pipeline
python pass1_article_fetching.py --list-id 1
python pass2_pdf_finding.py --list-id 1  
python pass3_pdf_verification.py --list-id 1

# 4. Generate reports
python reports.py summary
python reports.py publisher-stats
python reports.py export --list-id 1 --format csv
```

### Parallel Processing Example

```bash
# Split large list across multiple processes/machines
python pass2_pdf_finding.py --list-id 1 --start-index 0 --end-index 10000 &
python pass2_pdf_finding.py --list-id 1 --start-index 10000 --end-index 20000 &
python pass2_pdf_finding.py --list-id 1 --start-index 20000 --end-index 30000 &
```

### PMID List Management

```bash
# View list statistics
python pmid_manager.py stats --list-id 1

# Export PMID list
python pmid_manager.py export --list-id 1 --output exported_pmids.txt

# Create empty list for manual additions
python pmid_manager.py create --name "Manual Test" --description "Hand-picked PMIDs"
```

## Monitoring and Logs

All scripts generate detailed logs in the `log/` directory:

- `pass1_article_fetching.log`
- `pass2_pdf_finding.log`
- `pass3_pdf_verification.log`
- `pmid_manager.log`
- `database.log`

## Performance Considerations

- **Database Connection Pooling**: Configured via environment variables
- **Batch Processing**: Progress saved frequently to enable resuming
- **Memory Usage**: Streaming processing to handle large datasets
- **Network Timeouts**: Configurable timeouts with retry logic

## Migration from JSON-based System

The new system is designed to replace the JSON-based multipass system with these advantages:

1. **Persistent Storage**: All data stored in PostgreSQL
2. **Better Resume Logic**: Database-backed progress tracking
3. **Scalability**: Handle millions of PMIDs efficiently
4. **Analytics**: Rich querying and reporting capabilities
5. **Reliability**: ACID transactions and data integrity

## Troubleshooting

### Database Connection Issues
```bash
# Test database connection
python database.py --test

# Reinitialize schema if needed
python database.py --init
```

### Resume Not Working
- Check that PMID lists match between runs
- Verify database contains expected progress data
- Use `--start-index` for manual resume control

### Performance Issues
- Increase `--report-every` for less frequent progress reports
- Use `--timeout` to adjust HTTP timeouts for slow PDFs
- Consider parallel processing for large datasets

## Environment Variables

```bash
export FINDIT_DB_HOST=localhost
export FINDIT_DB_PORT=5432
export FINDIT_DB_NAME=findit_coverage
export FINDIT_DB_USER=postgres
export FINDIT_DB_PASSWORD=your_password
```

## Support

For issues and questions:
1. Check the log files in `log/` directory
2. Use `python reports.py runs` to see processing history
3. Refer to the metapub documentation for FindIt-specific issues