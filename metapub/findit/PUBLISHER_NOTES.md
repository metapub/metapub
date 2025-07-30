# Publisher Analysis Notes

This file documents research on publishers to avoid duplicate work when expanding the FindIt journal registry.

## Publishers Available via PMC (No FindIt integration needed)

These publishers' articles are already accessible through PubMed Central, so they don't need to be added to the FindIt registry:

- **IEEE** (402 journals, 641 PMIDs tested) - All articles found to be available via PMC
  - Analysis date: 2025-07-30
  - Test file: `output/publishers_clean/IEEE_PMIDs.txt`

- **PubMed Central (PMC)** (6 journals, 10 PMIDs tested) - DOIs resolve directly to PMC pages
  - Analysis date: 2025-07-30
  - Test file: `output/publishers_clean/PubMed_Central_PMC.txt`
  - Journals: BMJ Simul Technol Enhanc Learn, Bull World Health Organ, J Biomol Tech, JSLS, West J Med, Yale J Biol Med

## Publishers Integrated into FindIt Registry

These publishers have been successfully integrated with their journal lists expanded:

- **ScienceDirect** - Updated from 742 to 2,702 journals (+1,960)
- **Springer** - Updated from 464 to 2,353 journals (+1,889)  
- **Wiley** - Updated from 518 to 1,751 journals (+1,233)
- **BioMed Central (BMC)** - Updated from 6 to 366 journals (+360)
- **Karger** - Updated from 83 to 211 journals (+128)

## Complex Publishers (Require Special Handling)

These publishers require journal-specific mappings or complex URL patterns:

- **Oxford University Press** - 507 journals, 860 PMIDs
  - Analysis date: 2025-07-30
  - Current status: 26 journals already integrated via VIP system in `misc_vip.py`
  - Challenge: Each journal requires specific hostname mapping (e.g., `brain.oxfordjournals.org`, `jnci.oxfordjournals.org`)
  - URL Pattern: `http://{host}/content/{volume}/{issue}/{first_page}.full.pdf`
  - Strategy needed: Research hostname mappings for remaining 481 journals or test if Oxford now uses DOI redirects
  - Files: `output/publishers_clean/Oxford_University_Press.txt`, `Oxford_University_Press_PMIDs.txt`

## Publishers Requiring Further Analysis

Publishers in `output/publishers_clean/` that still need evaluation:

- **Cambridge University Press** - 253 journals, needs URL pattern analysis
- **Nature Publishing Group** - Likely requires special handling
- **SAGE Publications** - 916 journals, needs URL pattern analysis

## Analysis Methodology

1. **Simple Publishers**: Can construct PDF URLs using only PubMedArticle data (DOI, volume, issue, pages)
2. **Complex Publishers**: Require additional mappings (journal codes, special identifiers)
3. **PMC Available**: Articles accessible through PubMed Central, no FindIt integration needed

## Notes

- Focus on "simple" publishers first for maximum impact with minimal complexity
- Always test a sample of PMIDs before full integration
- Document URL construction patterns for each publisher
- Maintain backward compatibility with existing journal lists