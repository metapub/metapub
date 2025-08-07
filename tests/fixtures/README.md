# Test Fixtures

This directory contains XML fixtures for testing dance functions with real PubMed data.

## XML Fixtures Approach

Instead of mocking PubMedFetcher or creating artificial Mock objects, we:

1. **Download real XML once** using `PubMedFetcher.qs.efetch()`
2. **Save as test fixtures** in `pmid_xml/`
3. **Load with `PubMedArticle(xml)`** in tests

## Benefits

✅ **Real article metadata** (no mock mismatches)
✅ **No network dependencies** in tests  
✅ **Authentic test data** matching verified PMID system
✅ **Faster test execution** (no API calls)
✅ **Offline test capability**

## Usage

```python
from tests.fixtures import load_pmid_xml, EVIDENCE_PMIDS

# Load real PMA from XML fixture
pma = load_pmid_xml('35108047')
assert pma.journal == 'Sci Adv'
assert pma.doi == '10.1126/sciadv.abl6449'
```

## Adding New Fixtures

```python
from metapub import PubMedFetcher

fetch = PubMedFetcher()
xml_data = fetch.qs.efetch({'db': 'pubmed', 'id': 'YOUR_PMID'})

# Convert bytes to string if needed
if isinstance(xml_data, bytes):
    xml_data = xml_data.decode('utf-8')

# Save to fixture
with open(f'tests/fixtures/pmid_xml/YOUR_PMID.xml', 'w') as f:
    f.write(xml_data)
```

## Current Fixtures

Evidence PMIDs for AAAS (Science) journals:
- `35108047.xml` - Science Advances (`10.1126/sciadv.abl6449`)
- `37552767.xml` - Science Signaling (`10.1126/scisignal.ade0385`) 
- `37729413.xml` - Science Advances (`10.1126/sciadv.adi3902`)
- `37883555.xml` - Science (`10.1126/science.adh8285`)
- `39236155.xml` - Science (`10.1126/science.adn0327`)