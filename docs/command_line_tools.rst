Command Line Tools
==================

Metapub includes several command-line utilities for common tasks. These tools are installed automatically when you install metapub and can be used directly from your terminal.

Available Tools
---------------

The following command-line tools are available after installing metapub:

- ``ncbi_health_check`` - Check NCBI service status and diagnose issues
- ``pubmed_article`` - Fetch and display PubMed articles by PMID
- ``convert`` - Convert between publication identifiers (PMID, DOI, etc.)

NCBI Health Check
-----------------

A diagnostic tool to check the status of NCBI services that metapub depends on. Uses metapub's existing eutils client with built-in rate limiting and automatic NCBI_API_KEY support for reliable results.

**Quick Start**

.. code-block:: bash

   # Check essential services only (faster)
   ncbi_health_check --quick
   
   # Check all services
   ncbi_health_check
   
   # JSON output for automation
   ncbi_health_check --json

**Installation**

The health checker is included with metapub. After installing metapub with ``pip install metapub``, the command is immediately available.

**What It Checks**

*Essential Services (--quick mode)*
   - **EFetch** - PubMed article retrieval
   - **ESearch** - PubMed search functionality  
   - **ELink** - Related articles lookup
   - **ESummary** - Article summary data

*Additional Services (full check)*
   - **EInfo** - Database information
   - **MedGen Search** - Medical genetics database
   - **PMC Fetch** - PubMed Central articles
   - **NCBI Books** - Books database
   - **NCBI Main Website** - General availability

**Command Line Options**

.. code-block:: bash

   ncbi_health_check [OPTIONS]

   Options:
     --quick         Check only essential services (faster)
     --json          Output results as JSON for automation
     --timeout N     Set request timeout in seconds (default: 10)
     --no-details    Hide detailed response information

**Example Output**

*Normal Operation:*

.. code-block:: text

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

*Service Outage:*

.. code-block:: text

   🚨 CRITICAL: Core PubMed services are down. Tests will likely fail.
      Consider using FORCE_NETWORK_TESTS=1 only if you need to debug specific issues.

**Exit Codes**

- ``0`` - All services up and running normally
- ``1`` - Some services are down or have errors
- ``2`` - Some services are slow but functional

**JSON Output Format**

.. code-block:: json

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

**Integration with Testing**

The health checker powers automatic test skipping in metapub's test suite:

.. code-block:: bash

   # Tests automatically skip network tests when NCBI is down
   pytest tests/
   
   # Force tests to run anyway (they will likely fail)
   FORCE_NETWORK_TESTS=1 pytest tests/
   
   # Check service status before running tests manually
   ncbi_health_check --quick && pytest tests/

**Use Cases**

- **Before running tests** - Check if NCBI services are available
- **CI/CD pipelines** - Skip network tests when services are down
- **Debugging** - Identify which specific NCBI services are having issues
- **Monitoring** - Automated health checking in scripts
- **Development** - Quick status check during development

**Status Indicators**

- ✅ **UP** - Service responding normally
- 🐌 **SLOW** - Service responding but taking >5 seconds
- ❌ **DOWN** - Service not responding or returning errors
- ⚠️ **ERROR** - Service responding but with API errors

PubMed Article Fetcher
----------------------

Fetch and display PubMed articles by PMID from the command line.

**Usage**

.. code-block:: bash

   pubmed_article <pmid>

**Options**

.. code-block:: bash

   pubmed_article [OPTIONS] <pmid>

   Arguments:
     pmid            PubMed ID of the article to fetch

   Options:
     -h, --help      Print help screen
     -v, --version   Print the version of this program
     -a, --abstract  Include the abstract
     -f, --full      Print the full article, if possible (experimental)

**Examples**

.. code-block:: bash

   # Fetch basic article information
   pubmed_article 33157158
   
   # Include abstract
   pubmed_article -a 33157158
   
   # Full article (experimental)
   pubmed_article -f 33157158

**Sample Output**

.. code-block:: text

   Title: CRISPR-Cas9 gene editing for sickle cell disease and β-thalassemia
   Authors: Frangoul H, Altshuler D, Cappellini MD, Chen YS, Domm J, Eustace BK, ...
   Journal: New England Journal of Medicine
   Year: 2021
   DOI: 10.1056/NEJMoa2031054
   PMID: 33157158

Identifier Converter
--------------------

Convert between different publication identifiers (PMID, DOI, etc.).

**Usage**

.. code-block:: bash

   convert [OPTIONS] <identifier>

**Options**

.. code-block:: bash

   convert [OPTIONS] <identifier>

   Arguments:
     identifier      The identifier to convert (PMID, DOI, etc.)

   Options:
     -h, --help         Print help screen
     -v, --version      Print the version of this program
     --to-pmid         Convert to PMID
     --to-doi          Convert to DOI
     --to-pmc          Convert to PMC ID

**Examples**

.. code-block:: bash

   # Convert DOI to PMID
   convert --to-pmid 10.1056/NEJMoa2031054
   
   # Convert PMID to DOI
   convert --to-doi 33157158
   
   # Convert PMID to PMC ID
   convert --to-pmc 33157158

**Sample Output**

.. code-block:: text

   Input: 10.1056/NEJMoa2031054 (DOI)
   PMID: 33157158

Development and Automation
--------------------------

**Scripting with Health Check**

.. code-block:: bash

   #!/bin/bash
   # Check NCBI status before running data collection
   
   if ncbi_health_check --quick; then
       echo "NCBI services are up, starting data collection..."
       python my_metapub_script.py
   else
       echo "NCBI services are down, skipping collection"
       exit 1
   fi

**CI/CD Integration**

.. code-block:: yaml

   # GitHub Actions example
   - name: Check NCBI Services
     run: |
       if ! ncbi_health_check --quick; then
         echo "NCBI services down, skipping tests"
         exit 0
       fi
   
   - name: Run Tests
     run: pytest tests/

**JSON Processing**

.. code-block:: bash

   # Use jq to process JSON output
   ncbi_health_check --json | jq '.summary.up'
   
   # Check if all services are up
   if [ $(ncbi_health_check --json | jq '.summary.down + .summary.error') -eq 0 ]; then
       echo "All services operational"
   fi

**Python Module Usage**

All command-line tools can also be run as Python modules:

.. code-block:: bash

   # Alternative ways to run the tools
   python -m metapub.ncbi_health_check --quick
   python -m metapub.pubmedfetcher_cli 33157158
   python -m metapub.convert --to-doi 33157158

Troubleshooting
---------------

**Common Issues**

*Command not found*
   - Ensure metapub is installed: ``pip install metapub``
   - Check your PATH includes Python scripts directory
   - Try using the Python module syntax: ``python -m metapub.ncbi_health_check``

*Health check shows services down*
   - Check your internet connection
   - Verify you're not behind a restrictive firewall
   - Visit https://www.ncbi.nlm.nih.gov/ directly to confirm NCBI status
   - Try again in a few minutes (NCBI occasionally has brief outages)

*Timeouts or slow responses*
   - Increase timeout: ``ncbi_health_check --timeout 30``
   - Check your network connection
   - NCBI services may be experiencing high load

**Getting Help**

- Use ``--help`` flag with any command for detailed usage information
- Check the main documentation at `metapub.org <http://metapub.org>`_
- Report issues at `GitHub Issues <https://github.com/metapub/metapub/issues>`_