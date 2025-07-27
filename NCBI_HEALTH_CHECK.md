# NCBI Health Check Utility

A standalone command-line tool to check the status of NCBI services that metapub depends on.

## Quick Start

```bash
# After installing metapub, use the console command:
ncbi_health_check --quick

# Or run as Python module:
python -m metapub.ncbi_health_check --quick

# JSON output for scripts/automation
ncbi_health_check --json
```

## Installation

The health checker is included with metapub. After installing metapub with `pip install metapub`, you can run:

```bash
ncbi_health_check --quick
```

## What It Checks

### Essential Services (--quick mode)
- **EFetch** - PubMed article retrieval
- **ESearch** - PubMed search functionality  
- **ELink** - Related articles lookup
- **ESummary** - Article summary data

### Additional Services (full check)
- **EInfo** - Database information
- **MedGen Search** - Medical genetics database
- **PMC Fetch** - PubMed Central articles
- **NCBI Books** - Books database
- **NCBI Main Website** - General availability

## Output Examples

### Normal Output
```
🏥 NCBI SERVICE HEALTH CHECK REPORT
================================================================================

📊 SUMMARY: 4 services checked
   ✅ UP: 4

📋 DETAILED RESULTS:
--------------------------------------------------------------------------------
✅ EFetch (PubMed Articles)
   URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi
   Status: UP
   HTTP: 200
   Response Time: 0.45s
```

### Service Outage
```
🚨 CRITICAL: Core PubMed services are down. Tests will likely fail.
   Consider using FORCE_NETWORK_TESTS=1 only if you need to debug specific issues.
```

## Integration with Testing

This utility powers the automatic test skipping in metapub's test suite:

```bash
# Tests automatically skip network tests when NCBI is down
pytest tests/

# Force tests to run anyway (they will likely fail)
FORCE_NETWORK_TESTS=1 pytest tests/

# Check service status before running tests manually
python ncbi_health_check.py --quick && pytest tests/
```

## Command Line Options

- `--quick` - Check only essential services (faster)
- `--json` - Output results as JSON for automation
- `--timeout N` - Set request timeout in seconds (default: 10)
- `--no-details` - Hide detailed response information

## Exit Codes

- `0` - All services up and running normally
- `1` - Some services are down or have errors
- `2` - Some services are slow but functional

## JSON Output Format

```json
{
  "timestamp": 1234567890.123,
  "summary": {
    "total": 4,
    "up": 3,
    "slow": 1,
    "down": 0,
    "error": 0
  },
  "services": [
    {
      "name": "EFetch (PubMed Articles)",
      "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
      "status": "up",
      "response_time": 0.45,
      "status_code": 200,
      "error_message": null,
      "details": "Response time: 0.45s"
    }
  ]
}
```

## Use Cases

- **Before running tests** - Check if NCBI services are available
- **CI/CD pipelines** - Skip network tests when services are down
- **Debugging** - Identify which specific NCBI services are having issues
- **Monitoring** - Automated health checking in scripts
- **Development** - Quick status check during development

## Status Indicators

- ✅ **UP** - Service responding normally
- 🐌 **SLOW** - Service responding but taking >5 seconds
- ❌ **DOWN** - Service not responding or returning errors
- ⚠️ **ERROR** - Service responding but with API errors