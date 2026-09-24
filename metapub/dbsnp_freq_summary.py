"""Parser for dbSNP efetch/esummary DocumentSummary responses focused on MAFs.

Provides `DbSnpFreqSummary` that extracts study-level MAF information and
exposes convenience methods used by the ClinVar tooling.

See metapub.snp (previously) for background; this module is a rename to
make the frequency-focus explicit.
"""

from typing import Any, Dict, List, Optional, Tuple
from lxml import etree

from .exceptions import MetaPubError


class DbSnpFreqSummary:
    def __init__(self, xmlstr: str):
        try:
            dom = etree.fromstring(xmlstr.encode("utf-8") if isinstance(xmlstr, str) else xmlstr)
        except Exception as e:
            raise MetaPubError(f"Invalid XML for SNP esummary: {e}")

        # DocumentSummary may be nested under a DocumentSummarySet
        doc = None
        if dom.tag == 'DocumentSummarySet':
            doc = dom.find('.//DocumentSummary')
        elif dom.tag == 'DocumentSummary':
            doc = dom
        else:
            tmp = dom.find('.//DocumentSummary')
            doc = tmp if tmp is not None else dom

        if doc is None:
            raise MetaPubError('No DocumentSummary element found in SNP esummary')

        self.doc = doc

        # Inline extraction of element text for commonly-used fields.
        # We avoid a separate helper method and perform the minimal
        # existence/text checks inline so callers see exactly how
        # missing values are handled.

        spdi_elem = self.doc.find('SPDI')
        if spdi_elem is not None and spdi_elem.text is not None:
            # SPDI is typically like 'NC_000004.12:56911778:C:T'
            self.spdi = spdi_elem.text.strip()
        else:
            self.spdi = None

        docsum_elem = self.doc.find('DOCSUM')
        if docsum_elem is not None and docsum_elem.text is not None:
            # DOCSUM contains a short summary string; we keep it raw
            # (trimmed) for downstream heuristics.
            self.docsum = docsum_elem.text.strip()
        else:
            self.docsum = None

        snp_id_elem = self.doc.find('SNP_ID')
        if snp_id_elem is not None and snp_id_elem.text is not None:
            self.snp_id = snp_id_elem.text.strip()
        else:
            self.snp_id = None

        # Cache parsed GLOBAL_MAFS entries
        self._maf_elems = list(self.doc.findall('.//GLOBAL_MAFS/MAF'))

    def get_studies(self) -> Dict[str, Dict[str, Any]]:
        """Return a mapping of study -> {'global': {...}, 'subpopulations': [...]}

        The returned 'global' and subpopulation dicts use the simplified
        frequency summary shape documented above.
        """
        studies: Dict[str, Dict[str, Any]] = {}

        for maf in self._maf_elems:
            study_elem = maf.find('STUDY')
            if study_elem is None or study_elem.text is None:
                continue
            study = study_elem.text.strip()

            # pick the first FREQ as the study-global value (common in NCBI output)
            freq_elem = maf.find('FREQ')
            allele = None
            freq_val = None
            sample_size = None

            # Inline frequency token parsing. Typical format is:
            #   'T=0.300319/1504' -> allele='T', frequency=0.300319, sample_size=1504
            if freq_elem is not None and freq_elem.text:
                freq_text = freq_elem.text.strip()

                # Split off allele if present (text before '=')
                rest = freq_text
                if '=' in freq_text:
                    allele_part, rest_part = freq_text.split('=', 1)
                    allele = allele_part.strip()
                    rest = rest_part.strip()

                # If a sample size is present it follows a '/'
                if '/' in rest:
                    freq_str, sample_str = rest.split('/', 1)
                    freq_str = freq_str.strip()
                    sample_str = sample_str.strip()
                    try:
                        sample_size = int(sample_str)
                    except Exception:
                        sample_size = None
                else:
                    freq_str = rest.strip()

                # Parse frequency as float if possible
                try:
                    freq_val = float(freq_str)
                except Exception:
                    freq_val = None

            studies.setdefault(study, {'global': None, 'subpopulations': []})
            studies[study]['global'] = {
                'allele': allele,
                'frequency': freq_val,
                'population': sample_size or 0,
            }

            # Collect obvious nested subpopulation blocks if present (best-effort).
            subpops: List[Dict[str, Any]] = []
            # look for child MAF/POPULATION elements
            for child in maf.findall('MAF') + maf.findall('POPULATION'):
                # child may itself contain STUDY/FREQ pairs
                sub_study = child.find('STUDY')
                sub_freq = child.find('FREQ')
                if sub_freq is None or sub_freq.text is None:
                    continue

                # Inline parsing for the subpopulation frequency token
                sub_allele = None
                sub_freq_val = None
                sub_sample = None
                sub_freq_text = sub_freq.text.strip()

                # allele may be present before '='
                rest = sub_freq_text
                if '=' in sub_freq_text:
                    allele_part, rest_part = sub_freq_text.split('=', 1)
                    sub_allele = allele_part.strip()
                    rest = rest_part.strip()

                if '/' in rest:
                    freq_str, sample_str = rest.split('/', 1)
                    freq_str = freq_str.strip()
                    sample_str = sample_str.strip()
                    try:
                        sub_sample = int(sample_str)
                    except Exception:
                        sub_sample = None
                else:
                    freq_str = rest.strip()

                try:
                    sub_freq_val = float(freq_str)
                except Exception:
                    sub_freq_val = None

                subpops.append({
                    'study': sub_study.text.strip() if sub_study is not None and sub_study.text else None,
                    'allele': sub_allele,
                    'frequency': sub_freq_val,
                    'population': sub_sample or 0,
                })

            studies[study]['subpopulations'] = subpops

        return studies

    def get_global(self, study_id: str) -> Optional[Dict[str, Any]]:
        """Return the 'global' frequency summary for a given study.

        Output matches the requested final JSON shape:

            { population, ref_allele, ref_allele_freq, alt_allele, alt_allele_freq }
        """
        studies = self.get_studies()
        if study_id not in studies:
            return None

        global_row = studies[study_id]['global']
        if global_row is None:
            return None

        allele_in_freq = global_row.get('allele')
        freq_val = global_row.get('frequency')
        population = global_row.get('population', 0)

        # Determine reference and alternate alleles inline, preferring SPDI.
        # SPDI is canonical (e.g. 'NC_000004.12:56911778:C:T'), where the
        # last two ':'-separated fields are reference and alternate.
        ref = None
        alt = None
        if self.spdi:
            parts = self.spdi.split(':')
            if len(parts) >= 2:
                ref = parts[-2]
                alt = parts[-1]

        # If SPDI is missing, try to extract a SEQ=[ref/alt] token from DOCSUM
        if (ref is None and alt is None) and self.docsum:
            import re
            m = re.search(r'SEQ=\[([^\]]+)\]', self.docsum)
            if m:
                seq = m.group(1)
                if '/' in seq:
                    a, b = seq.split('/', 1)
                    ref = a.strip()
                    alt = b.strip()

        # Derive ref/alt frequencies using the best available information
        ref_freq = None
        alt_freq = None
        if allele_in_freq and freq_val is not None:
            if alt and allele_in_freq == alt:
                alt_freq = freq_val
                ref_freq = 1.0 - alt_freq if alt_freq is not None else None
            elif ref and allele_in_freq == ref:
                ref_freq = freq_val
                alt_freq = 1.0 - ref_freq if ref_freq is not None else None
            else:
                # allele present but does not match SPDI ref/alt.
                # Be conservative: record the allele and its frequency,
                # but do NOT infer the complementary allele frequency.
                alt = allele_in_freq
                alt_freq = freq_val
                ref_freq = None
        else:
            # No allele-specific freq present; attempt to use GLOBAL_SAMPLESIZE or fallback
            alt = alt or None
            ref = ref or None

        return {
            'population': int(population or 0),
            'ref_allele': ref,
            'ref_allele_freq': ref_freq,
            'alt_allele': alt,
            'alt_allele_freq': alt_freq,
        }

    def get_subpopulations(self, study_id: str) -> List[Dict[str, Any]]:
        """Return a list of subpopulation summaries for the given study.

        Each entry mirrors the smaller shape used in `get_studies()` subpop items.
        """
        studies = self.get_studies()
        if study_id not in studies:
            return []
        return studies[study_id].get('subpopulations', [])
