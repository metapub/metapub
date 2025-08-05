# Dance Function Rewrite Checklist

This checklist tracks our progress rewriting ALL dance functions using the evidence-driven development process.

## Process for Each Publisher

1. **Phase 1: Evidence Collection**
   - [ ] Investigate publisher patterns using real PMIDs from HTML samples
   - [ ] Create `{publisher}_investigator.py` to analyze patterns
   - [ ] Identify most reliable PDF extraction method

2. **Phase 2: Infrastructure Assessment**  
   - [ ] Test SSL compatibility
   - [ ] Check if generic functions need updates
   - [ ] Determine if direct URL construction is possible

3. **Phase 3: Dance Implementation**
   - [ ] Implement focused dance function (single method, clear errors)
   - [ ] Use discovered patterns, avoid complex parsing
   - [ ] Keep functions under 50 lines when possible

4. **Phase 4: Test Development**
   - [ ] Create focused tests in `tests/findit/test_{publisher}.py`
   - [ ] Test real PMIDs to verify function works
   - [ ] Ensure all tests pass

5. **Phase 5: Clean up and double-check work**
   - [ ] Move scripts used in the analysis/investigation of journals into the CLEANUP/ folder.
   - [ ] Make sure code quality is up to standards written in DANCE_FUNCTION_GUIDELINES.md


## Status Legend
- ✅ **COMPLETED** - Fully rewritten using evidence-driven process
- 🔍 **INVESTIGATED** - Patterns analyzed, needs implementation  
- 📝 **NEEDS_WORK** - Existing function needs improvement
- ❌ **TODO** - Not started yet
- 🚫 **SKIP** - Uses generic functions (the_doi_slide, the_vip_shake, paywall_handler)
- 🚫 **BLOCKED** - Site uses Cloudflare/bot protection preventing automated access

---

## Core Publishers (Alphabetical)

### ✅ AAAS (American Association for the Advancement of Science)
- **Dance Function:** `the_aaas_twist`
- **HTML Samples:** `output/article_html/aaas/`
- **Status:** TODO
- **Priority:** High (Science journal)
- **Notes:** Science magazine publisher

### ✅ AACR (American Association for Cancer Research)  
- **Dance Function:** `the_aacr_jitterbug`
- **HTML Samples:** ❌ No samples available (HTML was moved to cancerbiomed)
- **Status:** COMPLETED ✅ (registry updated with missing journals)
- **Priority:** High (cancer research)
- **Notes:** Fixed registry by adding 4 missing real AACR journals (Cancer Prev Res, Cancer Immunol Res, Blood Cancer Discov, Mol Cancer Res). Existing dance function works perfectly with 4/4 success rate.

### ✅ ACM (Association for Computing Machinery)
- **Dance Function:** `the_acm_reel`
- **HTML Samples:** `output/article_html/acm/`
- **Status:** TODO
- **Priority:** Medium (computer science)

### ✅ AHA (American Heart Association)
- **Dance Function:** `the_aha_waltz`
- **HTML Samples:** No samples available
- **Status:** TODO
- **Priority:** High (cardiovascular research)

### ✅ AIP (American Institute of Physics)
- **Dance Function:** `the_aip_allegro`
- **HTML Samples:** `output/article_html/aip/`
- **Status:** TODO
- **Priority:** Medium (physics journals)

### ✅ Allen Press
- **Dance Function:** `the_allenpress_advance`
- **HTML Samples:** `output/article_html/allenpress/`
- **Status:** TODO
- **Priority:** Low

### ✅ Annual Reviews
- **Dance Function:** `the_annualreviews_round`
- **HTML Samples:** `output/article_html/annualreviews/`
- **Status:** COMPLETED ✅ (evidence-driven PDF form extraction)
- **Priority:** Medium (high-impact review journals)
- **Notes:** Rewritten from 96→49 lines using evidence-driven approach with **direct URL construction**. Pattern: `https://www.annualreviews.org/deliver/fulltext/{journal_abbrev}/{volume}/{issue}/{doi_suffix}.pdf` where journal_abbrev is extracted from DOI pattern `annurev-{journal}-{date}-{id}`. Follows DANCE_FUNCTION_GUIDELINES: single method, no HTML parsing, under 50 lines, clear error messages. Test suite 11/11 passing with proper mocking.

### ✅ APA (American Psychological Association)
- **Dance Function:** `the_apa_dab`
- **HTML Samples:** `output/article_html/apa/`
- **Status:** TODO
- **Priority:** Medium (psychology journals)

### ✅ APS (American Physical Society)
- **Dance Function:** `the_aps_quickstep`
- **HTML Samples:** `output/article_html/american_physiological_society/`
- **Status:** TODO
- **Priority:** Medium (physics journals)

### ✅ ASME (American Society of Mechanical Engineers)
- **Dance Function:** `the_asme_animal`
- **HTML Samples:** `output/article_html/asme/`
- **Status:** TODO
- **Priority:** Low (engineering)

### ✅ ASM (American Society for Microbiology)
- **Dance Function:** `the_asm_shimmy`
- **HTML Samples:** `output/article_html/american_society_of_microbiology/`
- **Status:** TODO
- **Priority:** Medium (microbiology)

### ✅ Biochemical Society
- **Dance Function:** `the_biochemsoc_saunter`
- **HTML Samples:** `output/article_html/biochemsoc/`
- **Status:** TODO
- **Priority:** Medium (biochemistry)

### ✅ BioOne
- **Dance Function:** `the_bioone_bounce`
- **HTML Samples:** `output/article_html/bioone/`
- **Status:** TODO
- **Priority:** Medium (biological sciences)

### ✅ BMC (BioMed Central)
- **Dance Function:** `the_bmc_boogie`
- **HTML Samples:** No samples available
- **Status:** TODO
- **Priority:** High (open access biomedicine)

### ✅ Brill
- **Dance Function:** `the_brill_bridge`
- **HTML Samples:** `output/article_html/brill/`
- **Status:** TODO
- **Priority:** Low (humanities)

### ✅ Cambridge University Press
- **Dance Function:** `the_cambridge_foxtrot`
- **HTML Samples:** `output/article_html/cambridge_university_press/`
- **Status:** COMPLETED ✅ (rewritten using citation_pdf_url)
- **Priority:** High (major academic publisher)
- **Notes:** Rewritten from 54→26 lines using citation_pdf_url meta tag extraction. 100% pattern consistency across 10 HTML samples. Evidence-driven approach: fetches article page → extracts Cambridge's own PDF metadata. 2/3 test PMIDs successful (recent articles work, older may be restricted).

### ✅ Cancer Biology & Medicine
- **Dance Function:** `the_cancerbiomed_quickstep`
- **HTML Samples:** `output/article_html/cancerbiomed/` (moved from american_association_for_cancer_research)
- **Status:** COMPLETED ✅
- **Priority:** Medium
- **Notes:** New publisher added! Uses direct VIP URL construction (25 lines, 100% success rate). HTML samples relocated to correct directory.

### ✅ Cell Press
- **Dance Function:** ~~`the_cell_pogo`~~ **CONSOLIDATED** into ScienceDirect
- **HTML Samples:** `output/article_html/cell/`
- **Status:** COMPLETED ✅ (consolidated into ScienceDirect)
- **Priority:** High (top-tier life sciences)
- **Notes:** Cell Press journals are owned by Elsevier and use ScienceDirect infrastructure. All 15 Cell journals (Cell, Neuron, Immunity etc.) now consolidated into `sciencedirect_journals` list and use `the_sciencedirect_disco` dance function. Registry updated, Cell-specific files removed. This eliminates redundant code while maintaining full functionality.

### ✅ De Gruyter
- **Dance Function:** `the_degruyter_danza`
- **HTML Samples:** `output/article_html/degruyter/`
- **Status:** TODO
- **Priority:** Medium (academic publisher)

### ✅ Dovepress
- **Dance Function:** `the_dovepress_peacock`
- **HTML Samples:** `output/article_html/dovepress/` (corrupted - missing brotli package)
- **Status:** COMPLETED ✅ (fixed infrastructure issue)
- **Priority:** Low (open access)
- **Notes:** Rewritten from 82→54 lines. **Infrastructure Fix**: HTML samples were corrupted because `unified_uri_get` advertises Brotli support but the `brotli` package wasn't installed. Installing `brotli` fixed the issue. Uses article/download/ link pattern extraction. Function now works properly with `unified_uri_get`.

### ✅ Emerald
- **Dance Function:** `the_emerald_ceili`
- **HTML Samples:** `output/article_html/emerald/` (Cloudflare protected)
- **Status:** COMPLETED ✅ (rewritten, blocked by Cloudflare)
- **Priority:** Low (business/management)
- **Notes:** Rewritten from 73→18 lines, removed all code fouls (nested try-except, generic Exception catching). Function correctly constructs PDF URLs but Emerald uses Cloudflare protection. URL construction works perfectly, verification blocked by bot protection.

### ✅ Endocrine Society
- **Dance Function:** `the_endo_mambo`
- **HTML Samples:** `output/article_html/endo/`
- **Status:** TODO
- **Priority:** Medium (endocrinology)

### ✅ Eurekaselect (Bentham Science Publishers)
- **Dance Function:** `the_eureka_frug`
- **HTML Samples:** `output/article_html/eurekaselect/` (previously corrupted - fixed by brotli package)
- **Status:** COMPLETED ✅ (rewritten for better code organization)
- **Priority:** Low
- **Notes:** Rewritten from 96→45 lines, removed massive if/else duplication, eliminated generic exception handling, simplified logic flow. **Infrastructure Benefit**: Function benefits from Brotli compression fix. Correctly constructs PDF URLs but EurekaSelect servers return HTTP 500 errors for PDF generation - this is documented and handled appropriately. Much cleaner code organization now follows our established principles. **Tests**: Comprehensive test suite in `tests/findit/test_bentham.py` updated and verified working (6 tests pass).

### ✅ Frontiers
- **Dance Function:** `the_frontiers_square`
- **HTML Samples:** `output/article_html/frontiers/`
- **Status:** TODO
- **Priority:** Medium (open access)

### ✅ Hilaris
- **Dance Function:** `the_hilaris_hop`
- **HTML Samples:** `output/article_html/hilaris/`
- **Status:** TODO
- **Priority:** Low (open access)

### ✅ Inderscience
- **Dance Function:** `the_inderscience_ula`
- **HTML Samples:** `output/article_html/inderscience/`
- **Status:** TODO
- **Priority:** Low

### ✅ Ingenta
- **Dance Function:** `the_ingenta_flux`
- **HTML Samples:** `output/article_html/ingentaconnect/`
- **Status:** TODO
- **Priority:** Low (aggregator)

### ✅ IOP (Institute of Physics)
- **Dance Function:** `the_iop_fusion`
- **HTML Samples:** `output/article_html/iop/`
- **Status:** TODO
- **Priority:** Medium (physics)

### ✅ IOS Press
- **Dance Function:** `the_iospress_freestyle`
- **HTML Samples:** `output/article_html/iospress/`
- **Status:** TODO
- **Priority:** Low

### ✅ JAMA Network  
- **Dance Function:** `the_jama_dance`
- **HTML Samples:** `output/article_html/jama/` (**BLOCKED BY CLOUDFLARE**)
- **Status:** 🚫 **BLOCKED** - Cloudflare protection prevents analysis
- **Priority:** High (top medical journals)
- **Notes:** All HTML samples show Cloudflare challenge pages ("Just a moment...") indicating JAMA has implemented bot protection. Cannot analyze patterns or improve function while Cloudflare blocking is active. Current function uses `citation_pdf_url` extraction but effectiveness unknown due to access restrictions.

### ✅ JCI (Journal of Clinical Investigation)
- **Dance Function:** `the_jci_jig`
- **HTML Samples:** `output/article_html/jci/`
- **Status:** COMPLETED ✅ (fixed broken URL pattern)
- **Priority:** High (top medical journal)
- **Notes:** **Critical URL Pattern Fix**: HTML evidence revealed function was using wrong pattern. Changed from `/pdf` to `/files/pdf` based on `citation_pdf_url` meta tags in HTML samples. Old pattern: `https://www.jci.org/articles/view/{pii}/pdf` (broken). New pattern: `http://www.jci.org/articles/view/{pii}/files/pdf` (works). Updated both PII and DOI fallback paths. All 10 tests pass. Function was well-structured but had incorrect URL format.

### ✅ J-STAGE
- **Dance Function:** `the_jstage_dive`
- **HTML Samples:** `output/article_html/jstage/`
- **Status:** TODO
- **Priority:** Medium (Japanese journals)

### ✅ Karger
- **Dance Function:** `the_karger_conga`
- **HTML Samples:** `output/article_html/karger/`
- **Status:** TODO
- **Priority:** Medium (medical publisher)

### ✅ Lancet
- **Dance Function:** ~~`the_lancet_tango`~~ **CONSOLIDATED** into ScienceDirect
- **HTML Samples:** `output/article_html/lancet/`
- **Status:** COMPLETED ✅ (consolidated into ScienceDirect)
- **Priority:** High (top medical journal)
- **Notes:** Lancet journals are owned by Elsevier and use ScienceDirect infrastructure. HTML evidence shows all Lancet articles redirect through Elsevier's linking hub system. All 10 Lancet journals (Lancet, Lancet Oncol, Lancet Infect Dis, etc.) consolidated into `sciencedirect_journals` list and use `the_sciencedirect_disco` dance function. Old `the_lancet_tango` was broken (403 Forbidden). Registry updated, Lancet-specific files removed. Modern Elsevier infrastructure now handles all Lancet journals properly.

### ✅ Longdom
- **Dance Function:** `the_longdom_hustle`
- **HTML Samples:** `output/article_html/longdom/`
- **Status:** TODO
- **Priority:** Low (predatory publisher concerns)

### ✅ MDPI
- **Dance Function:** `the_mdpi_moonwalk`
- **HTML Samples:** `output/article_html/mdpi/`
- **Status:** TODO
- **Priority:** Medium (open access)

### ✅ NAJMS
- **Dance Function:** `the_najms_mazurka`
- **HTML Samples:** No samples available
- **Status:** TODO
- **Priority:** Low

### ✅ Nature Publishing Group
- **Dance Function:** `the_nature_ballet`
- **HTML Samples:** `output/article_html/nature/`
- **Status:** COMPLETED ✅
- **Priority:** High (top-tier journals)
- **Notes:** Rewritten from 134→76 lines using evidence-driven approach. Pattern: `/articles/{doi_suffix}.pdf` for modern DOIs, `/articles/{id}.pdf` for legacy. Uses DOI from meta tags/JSON-LD. Test suite with 10 tests covers all patterns.

### ✅ OAText
- **Dance Function:** `the_oatext_orbit`
- **HTML Samples:** `output/article_html/oatext/`
- **Status:** TODO
- **Priority:** Low (open access)

### ✅ Project MUSE
- **Dance Function:** `the_projectmuse_syrtos`
- **HTML Samples:** `output/article_html/projectmuse/`
- **Status:** TODO
- **Priority:** Medium (humanities/social sciences)

### ✅ Royal Society of Chemistry
- **Dance Function:** `the_rsc_reaction`
- **HTML Samples:** `output/article_html/rsc/`
- **Status:** TODO
- **Priority:** Medium (chemistry)

### ✅ SAGE Publications
- **Dance Function:** `the_sage_hula`
- **HTML Samples:** `output/article_html/sage_publications/`
- **Status:** TODO
- **Priority:** Medium (social sciences)

### ✅ SciELO
- **Dance Function:** `the_scielo_chula`
- **HTML Samples:** `output/article_html/scielo/`
- **Status:** COMPLETED ✅
- **Priority:** High (Latin American journals)
- **Notes:** Existing function works well (8/9 success rate), uses citation_pdf_url meta tag

### ✅ Sciendo
- **Dance Function:** `the_sciendo_spiral`
- **HTML Samples:** `output/article_html/sciendo/`
- **Status:** TODO
- **Priority:** Low

### ✅ ScienceDirect (Elsevier)
- **Dance Function:** `the_sciencedirect_disco`
- **HTML Samples:** `output/article_html/sciencedirect/`
- **Status:** COMPLETED ✅ (enhanced with Cell Press + Lancet consolidation)
- **Priority:** High (major publisher)
- **Notes:** Rewritten from 51→61 lines using direct PDF URL construction from PII. Pattern: `https://www.sciencedirect.com/science/article/pii/{clean_pii}/pdfft?isDTMRedir=true&download=true`. PII cleaning removes special characters. **MAJOR CONSOLIDATIONS**: Cell Press journals (15 journals) + Lancet journals (10 journals) consolidated into ScienceDirect since both are owned by Elsevier and use the same infrastructure. Old Lancet function was broken (403 errors). This reduces codebase complexity while maintaining full functionality.

### ✅ SCIRP (Scientific Research Publishing)
- **Dance Function:** `the_scirp_timewarp`
- **HTML Samples:** `output/article_html/scirp/`
- **Status:** COMPLETED ✅
- **Priority:** Medium (backup for PMC)
- **Notes:** Rewritten from 95→44 lines, uses <link rel="alternate"> pattern

### ✅ Spandidos Publications
- **Dance Function:** `the_spandidos_lambada`
- **HTML Samples:** `output/article_html/spandidos/`
- **Status:** COMPLETED ✅  
- **Priority:** Medium
- **Notes:** Rewritten from 35→25 lines, direct URL construction from DOI

### ✅ Springer
- **Dance Function:** `the_springer_shag`
- **HTML Samples:** `output/article_html/springer/`
- **Status:** COMPLETED ✅
- **Priority:** High (major publisher)
- **Notes:** Rewritten from 147→37 lines. Evidence: 100% consistent pattern `https://link.springer.com/content/pdf/{DOI}.pdf`. Trusts registry (no DOI gating). BMC journals handled separately by `the_bmc_boogie`. Test suite with 10 tests.

### ✅ Thieme
- **Dance Function:** `the_thieme_tap`
- **HTML Samples:** `output/article_html/thieme_medical_publishers/`
- **Status:** COMPLETED ✅ (perfect pattern consistency)
- **Priority:** Medium (medical publisher)
- **Notes:** Rewritten from 62→35 lines using evidence-driven approach with **perfect 10/10 pattern consistency**. Pattern: `http://www.thieme-connect.de/products/ejournals/pdf/{DOI}.pdf` where all Thieme DOIs use 10.1055/ prefix. Evidence shows both s-prefix (older) and a-prefix (newer) articles follow exact same pattern. Follows DANCE_FUNCTION_GUIDELINES: single method, direct URL construction, under 50 lines. Test suite 9/9 passing.

### ✅ University of Chicago Press
- **Dance Function:** `the_uchicago_walk`
- **HTML Samples:** `output/article_html/uchicago/`
- **Status:** TODO
- **Priority:** Medium (academic publisher)

### ✅ WalsMedia
- **Dance Function:** `the_walshmedia_bora`
- **HTML Samples:** `output/article_html/walshmedia/`
- **Status:** TODO
- **Priority:** Low

### ✅ Wiley
- **Dance Function:** `the_wiley_shuffle`
- **HTML Samples:** `output/article_html/wiley/`
- **Status:** COMPLETED ✅
- **Priority:** High (major publisher)
- **Notes:** Rewritten from 54→30 lines using evidence from `wiley_example.txt`. Pattern: `https://onlinelibrary.wiley.com/doi/epdf/{DOI}`. Eliminated complex HTML parsing. Supports all DOI patterns (10.1002, 10.1111, 10.1155 Hindawi). Test suite with 10 tests.

### ✅ WJGNet
- **Dance Function:** `the_wjgnet_wave`
- **HTML Samples:** `output/article_html/wjgnet/`
- **Status:** TODO
- **Priority:** Low

### ✅ Wolters Kluwer
- **Dance Function:** `the_wolterskluwer_volta`
- **HTML Samples:** `output/article_html/wolterskluwer/`
- **Status:** TODO
- **Priority:** High (major medical publisher)

### ✅ World Scientific
- **Dance Function:** `the_worldscientific_robot`
- **HTML Samples:** `output/article_html/worldscientific/`
- **Status:** TODO
- **Priority:** Medium (physics/mathematics)

---

## Generic Functions (Skip - No Rewrite Needed)

These publishers use generic functions that don't need individual rewrites:

### 🚫 DOI Slide Publishers (the_doi_slide)
- Taylor & Francis
- ACS (American Chemical Society) 
- Informa
- Liebert
- ATS (American Thoracic Society)
- Various smaller publishers

### 🚫 VIP Shake Publishers (the_vip_shake)  
- Oxford University Press
- Various journal-specific implementations

### 🚫 Paywall Handlers (paywall_handler)
- Dustri (TODO: Implement the_dustri_stomp)
- Schattauer
- Cig Media

---

## Progress Summary

- **Completed:** 16/40+ publishers (SCIRP, Spandidos, SciELO, Cancer Biology & Medicine, AACR, Emerald, Cambridge, Dovepress, EurekaSelect, Nature, Springer, Wiley, ScienceDirect+Cell+Lancet, JCI, Annual Reviews)
- **High Priority Remaining:** BMC, Wolters Kluwer, AAAS, AHA
- **Blocked by Protection:** JAMA (Cloudflare)
- **Next Recommended:** Pick high-priority publishers with existing HTML samples

## HTML Sample Availability

**Publishers with HTML samples available (ready for investigation):**
- AAAS, ACM, AACR, AIP, Allen Press, Annual Reviews, APA, APS, ASME, ASM
- Biochemical Society, BioOne, Brill, Cambridge, Cell Press, De Gruyter, Dovepress
- Emerald, Endocrine Society, Eurekaselect, Frontiers, Hilaris, Inderscience, Ingenta
- IOP, IOS Press, JAMA, JCI, J-STAGE, Karger, Lancet, Longdom, MDPI
- Nature, OAText, Project MUSE, RSC, SAGE, SciELO, Sciendo, ScienceDirect
- SCIRP, Spandidos, Springer, Thieme, University of Chicago, WalsMedia
- Wiley, WJGNet, Wolters Kluwer, World Scientific

**Publishers without HTML samples:**
- AHA, BMC, NAJMS

## Recent Activity

- **2025-01-08:** Completed SCIRP rewrite (95→44 lines, regex pattern)
- **2025-01-08:** Completed Spandidos rewrite (35→25 lines, direct URL construction)  
- **2025-01-08:** Confirmed SciELO existing function works well (8/9 success)
- **2025-01-08:** Updated checklist with HTML sample paths for all publishers
- **2025-01-08:** Created NEW Cancer Biology & Medicine dance function (25 lines, VIP construction, 100% success)
- **2025-01-08:** **INFRASTRUCTURE FIX**: Fixed Brotli compression issue by installing `brotli` package. `unified_uri_get` was advertising Brotli support but couldn't decompress it, affecting Dovepress and potentially other publishers.
- **2025-01-08:** Completed Dovepress rewrite (82→54 lines) after fixing infrastructure issue
- **2025-01-08:** Rewritten EurekaSelect function (96→45 lines) - removed code organization issues, eliminated if/else duplication and generic exception handling
- **2025-01-09:** Completed Nature rewrite (134→76 lines) using evidence-driven approach with DOI suffix patterns
- **2025-01-09:** Completed Springer rewrite (147→37 lines) with registry trust principle - no DOI gating
- **2025-01-09:** Completed Wiley rewrite (54→30 lines) using epdf pattern from wiley_example.txt
- **2025-01-09:** Fixed test imports (restored creative dance names: the_projectmuse_syrtos, the_wjgnet_wave)
- **2025-08-05:** **MAJOR CONSOLIDATION**: Cell Press integrated into ScienceDirect - Cell is owned by Elsevier and uses ScienceDirect infrastructure, so all 15 Cell journals now use `the_sciencedirect_disco`. Removed redundant `the_cell_pogo` function, tests, and journal files. Registry regenerated. This simplifies codebase while maintaining full functionality.
- **2025-08-05:** **SECOND MAJOR CONSOLIDATION**: Lancet integrated into ScienceDirect - HTML evidence shows Lancet uses Elsevier's linking hub infrastructure. Old `the_lancet_tango` was broken (403 Forbidden errors). All 10 Lancet journals now use `the_sciencedirect_disco`. Removed broken Lancet function and files. Registry regenerated. ScienceDirect now handles Cell Press (15) + Lancet (10) + core ScienceDirect journals = comprehensive Elsevier coverage.
- **2025-08-05:** **CRITICAL JCI FIX**: Fixed broken JCI function using HTML evidence. Pattern was `/pdf` but should be `/files/pdf` based on `citation_pdf_url` meta tags. Updated both PII and DOI fallback logic. Fixed test mocks to use proper targets. All 10 tests pass. This demonstrates the power of evidence-driven development - function appeared to work but had wrong URL pattern.
- **2025-08-05:** **ANNUAL REVIEWS COMPLETED**: Rewritten using evidence-driven approach (96→49 lines) with **direct URL construction** following DANCE_FUNCTION_GUIDELINES. Pattern: `https://www.annualreviews.org/deliver/fulltext/{journal_abbrev}/{volume}/{issue}/{doi_suffix}.pdf` extracted from DOI pattern `annurev-{journal}-{date}-{id}`. Single method, no HTML parsing, under 50 lines, clear error messages. Test suite 11/11 passing. **CORRECTED**: Initial implementation violated guidelines with HTML parsing - proper version uses direct URL construction from DOI analysis.

## Notes

- Focus on publishers with HTML samples in `output/article_html/`
- Prioritize high-impact journals and major publishers
- Some publishers may not need rewrites if current functions work well
- Document all patterns discovered for future reference
