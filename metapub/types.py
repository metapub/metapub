"""metapub.types -- shared type definitions used across metapub modules."""

from typing import NotRequired, TypedDict
from enum import StrEnum


class XRefDb(StrEnum):
    """String enum of ``DB`` attribute values observed in ClinVar ``<XRef>`` nodes.

    Example node: ``<XRef ID="CA390882941" DB="ClinGen"/>``

    Full list at https://www.ncbi.nlm.nih.gov/clinvar/docs/identifiers/

    Use these constants instead of bare strings when filtering
    :attr:`ClinVarVariant.xrefs <metapub.clinvarvariant.ClinVarVariant.xrefs>`
    to avoid silent typos (e.g. ``XRefDB.DBSNP`` instead of ``'dbSNP'``).
    """
    CLINGEN = 'ClinGen'
    """ClinGen allele registry identifier."""
    DBSNP = 'dbSNP'
    """NCBI dbSNP rsID."""
    BOOKSHELF = 'BookShelf'
    """NCBI BookShelf reference."""
    DBVAR = 'dbVar'
    """NCBI dbVar structural variant identifier."""
    GENE = 'Gene'
    """NCBI Gene identifier."""
    MEDGEN = 'MedGen'
    """NCBI MedGen concept identifier (appears at condition level, not allele level)."""
    PUBMED = 'PubMed'
    """PubMed article identifier."""
    PUBMEDCENTRAL = 'PubMedCentral'
    """PubMed Central article identifier."""
    OMIM = 'OMIM'
    """Online Mendelian Inheritance in Man identifier."""
    ORPHANET = 'Orphanet'
    """Orphanet rare disease identifier (appears at condition level, not allele level)."""


class XRef(TypedDict):
    """Describes an ``<XRef>`` node parsed from ClinVar XML.

    Example node: ``<XRef Type="rs" ID="1555371642" DB="dbSNP"/>``

    :var ID: The cross-reference identifier (e.g. ``'28934872'``, ``'rs1799945'``).
    :vartype ID: str
    :var DB: The source database name (e.g. ``'dbSNP'``, ``'OMIM'``).
        Full list at https://www.ncbi.nlm.nih.gov/clinvar/docs/identifiers/
    :vartype DB: str
    :var Type: Optional sub-type qualifier (e.g. ``'rs'``, ``'rsNumber'``).
        Absent from some real ClinVar records — always use ``DB`` to identify the source.
    :vartype Type: str, optional
    """
    ID: str
    DB: str
    Type: NotRequired[str]
