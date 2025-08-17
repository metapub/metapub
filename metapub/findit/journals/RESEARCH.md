# FindIt Journal Research Notes

**Important**: This information needs further investigation and may be outdated. These notes were preserved during the migration from Python-based configurations to YAML-based publisher configurations.

## Discontinued Journals

The following journals are discontinued or otherwise inaccessible. This information was preserved from the CANTDO list:

### Historical Journals (Pre-1980s)
- **J Lancet** - Not to be confused with THE Lancet ("Lancet"), this journal ended in 1965, collection unlikely
- **Nat Monspel Ser Bot** - 1972-1973, [reference](https://www.unboundmedicine.com/medline/journal/Nat_Monspel_Ser_Bot)
- **Nat Law Forum** - Ended 1967, [search](https://www.ncbi.nlm.nih.gov/pubmed/?term=%22Nat+Law+Forum%22[TA])
- **Nat Mus** - Ended 1980, German language, [search](https://www.ncbi.nlm.nih.gov/pubmed/?term=%22Nat+Mus%22[TA])
- **Physiol Teach** - Ended 1977, not even look-up-able in AJP Legacy where you'd expect it: https://ajplegacy.physiology.org

### Recent Discontinued Journals (1980s-2000s)
- **Nat Prod Lett** - Ended 2002, [search](https://www.ncbi.nlm.nih.gov/pubmed/?term=%22Nat+Prod+Lett%22[TA])
- **Nat Hist** - Ended 1998, [search](https://www.ncbi.nlm.nih.gov/pubmed/?term=%22Nat+Hist%22[TA])
- **Nat Syst** - One article from 1982: [PMID 11617791](https://www.ncbi.nlm.nih.gov/pubmed/?term=11617791)
- **Nat Resour Forum** - Ended 1997, [search](https://www.ncbi.nlm.nih.gov/pubmed/?term=%22Nat+Resour+Forum%22[TA])
- **Nat Resour J** - Ended 1982, [search](https://www.ncbi.nlm.nih.gov/pubmed/?term=%22Nat+Resour+J%22[TA])

### Problematic Journals
- **Zhonghua Yi Xue Yi Chuan Xue Za Zhi** - Chinese language, DOI won't resolve (example: https://dx.doi.org/10.3760/cma.j.issn.1003-9406.2015.05.034)

## VIP Pattern Research Notes

**Pattern**: Volume-Issue-Page format URLs with consistent structure across publishers
**Standard format**: `http://{host}/content/{volume}/{issue}/{first_page}.full.pdf`

### Backup URL Strategies (PMID Lookup)
Several publishers support PMID-based article lookup that could serve as backup methods:

#### American Society for Microbiology (ASM)
- **Pattern**: `http://[journal].asm.org/cgi/pmidlookup?view=long&pmid=[PMID]`
- **Example**: http://aac.asm.org/cgi/pmidlookup?view=long&pmid=7689822
- **Example**: http://jb.asm.org/cgi/pmidlookup?view=long&pmid=7683021

#### Cold Spring Harbor Laboratory Press
- **Example**: http://emboj.embopress.org/cgi/pmidlookup?view=long&pmid=9501081
- **Example**: http://www.plantcell.org/cgi/pmidlookup?view=long&pmid=9501112

#### American Society for Biochemistry and Molecular Biology
- **Example**: http://www.jbc.org/cgi/pmidlookup?view=long&pmid=14722075

#### American Physiological Society
- **Example**: http://physiolgenomics.physiology.org/cgi/pmidlookup?view=long&pmid=15252189

#### Other Publishers with PMID Lookup
- **Blood**: http://www.bloodjournal.org/cgi/pmidlookup?view=long&pmid=1586703
- **Canadian Family Physician**: http://www.cfp.ca/cgi/pmidlookup?view=long&pmid=19282532
- **Journal of Nutrition**: http://jn.nutrition.org/cgi/pmidlookup?view=long&pmid=10736367
- **SAGE (JAH)**: http://jah.sagepub.com/cgi/pmidlookup?view=long&pmid=20056814

### Nonstandard VIP Patterns
Some journals use VIP-like patterns but with different URL structures:

#### Blood (American Society of Hematology)
- **Pattern**: `http://www.bloodjournal.org/content/bloodjournal/{volume}/{issue}/{first_page}.full.pdf`
- **Note**: Includes journal name in path structure

#### BMJ (British Medical Journal)
- **Pattern**: `http://www.bmj.com/content/bmj/350/bmj.h3317.full.pdf`
- **Note**: Includes journal abbreviation in path

#### Thorax (BMJ)
- **Early release example**: http://thorax.bmj.com/content/early/2015/06/23/thoraxjnl-2015-207199.full.pdf+html
- **Note**: Early release format variation

### Publisher-Specific Notes

#### Endocrinology-Related Content Transitions
- **Endocr Relat Cancer**: Host `erc.endocrinology-journals.org` → now `https://erc.bioscientifica.com/`
- **Note**: Publisher domain transitions need investigation

#### American Physiological Society Expansion
- **TODO**: Complete migration of all physiology.org journals
- **Reference**: http://www.the-aps.org/mm/Publications/Journals

#### Unhandled VIP Cases
- **BMJ Case Rep**: `{'host': 'casereports.bmj.com', 'example': 'http://casereports.bmj.com/content/2016/bcr-2015-214310'}`
- **Note**: Non-VIP pattern, needs special handling

## PII Pattern Research Notes

**Pattern**: Publisher Item Identifier-based URLs
**Standard format**: `http://[domain]/article/{pii}/pdf`

### Publisher Groups by Pattern

#### Elsevier Journals
Most PII-based journals appear to be Elsevier publications using consistent URL patterns:
- Standard pattern: `http://www.[journal-domain].com/article/{pii}/pdf`
- Examples: ajconline.org, ajo.com, amjmed.com, biologicalpsychiatryjournal.com

#### Non-Elsevier PII Publishers
- **Cancer Cell Int**: `http://www.cancerci.com/content/pdf/{pii}.pdf` (different path structure)
- **J Mol Diagn**: `http://jmd.amjpathol.org/article/{pii}/pdf` (American Society for Investigative Pathology)
- **Orv Hetil**: `http://www.akademiai.com/content/{pii}/fulltext.pdf` (Hungarian, different format)

### Domain-to-Publisher Mapping Research Needed
Many domains need investigation to identify actual publishers:
- ahjonline.com, ajconline.org, ajo.com, amjmed.com, atherosclerosis-journal.com
- arcmedres.com, biologicalpsychiatryjournal.com, thebonejournal.com
- brainanddevelopment.com, cancerci.com, cancergeneticsjournal.org
- cancerletters.info, clineu-journal.com, diabetesresearchclinicalpractice.com
- epires-journal.com, ejpn-journal.com, exphem.org, fertstert.org
- gastrojournal.org, gynecologiconcology-online.net, heartrhythmjournal.com
- ijporlonline.com, internationaljournalofcardiology.com, jdsjournal.com
- jmmc-online.com, jns-journal.com, jpeds.com, jpurol.com
- aaojournal.org, medical-hypotheses.com, metabolismjournal.com
- mgmjournal.com, neurobiologyofaging.org, nmd-journal.com
- prd-journal.com, pedneur.com, placentajournal.org, worldneurosurgery.org
- thrombosisresearch.com

### Migration Status
- **Elsevier journals**: Partially migrated to `misc_pii_elsevier.yaml`
- **Remaining journals**: Need publisher identification and proper YAML migration

## Next Steps

1. **Publisher Identification**: Research the actual publishers behind domain names
2. **Pattern Validation**: Verify current URL patterns are still valid
3. **Backup Strategy Implementation**: Consider implementing PMID lookup fallbacks
4. **Domain Transition Tracking**: Monitor publisher domain changes
5. **Early Release Handling**: Develop strategies for early release article access

## Migration History

- **2025-08-17**: Information preserved from `cantdo_list.py`, `misc_vip.py`, and `misc_pii.py`
- **Legacy Python configs**: Scheduled for deprecation after YAML migration completion