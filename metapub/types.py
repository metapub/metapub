"""metapub.types -- shared type definitions used across metapub modules."""

from typing import NotRequired, TypedDict
from enum import StrEnum
from typing import Optional, Literal
from dataclasses import dataclass


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

# See: https://www.ncbi.nlm.nih.gov/clinvar/docs/clinsig/
# All possible clinical significance classes a variant may be classified as
# by a submitter.
# 
# NOTE: here we represent clinical significance classes in lowercase.
ClinSig = Literal[
    "pathogenic", "likely pathogenic", "uncertain significance",
    "likely benign", "benign", "conflicting interpretations",
    "drug response", "risk factor", "association",
    "protective", "other", "likely pathogenic, low penetrance",
    "pathogenic, low penetrance",
    "uncertain risk allele", "likely risk allele",
    "established risk allele", "affects", "conflicting data from submitters",
    "not provided", "vus-high", "vus-mid", "vus-low"
]
# Possible types of IDs a user may supply to initialize a variant.
IdLocations = Literal['clinvar', 'entrez']

# Possible types of molecular consequences
# See here for list: https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g=clinvar
MolecularConsequences = Literal[
    "genic downstream transcript variant", "no sequence alteration",
    "inframe indel", "stop lost", "genic upstream transcript variant",
    "initiator codon variant", "inframe insertion", "inframe deletion",
    "splice acceptor variant", "splice donor variant", "5 prime UTR variant",
    "nonsense", "non-coding transcript variant", "3 prime UTR variant",
    "frameshift variant", "intron variant", "synonymous variant", "missense variant",
    "unknown", "initiator codon variant"
]

@dataclass
class PathogenicSummary:
    counts: dict[ClinSig, int]
    total_submitters: int
    consensus: Optional[ClinSig]
    conflicting: bool
    review_status: Optional[str]

@dataclass
class MolecularConsequenceInfo:
    type: Optional[MolecularConsequences]
    so_id: Optional[str]
    database: Optional[str]

@dataclass
class SPDIInfo:
    chromosome: int
    start_position: int
    deleted: str
    replaced: str
    version: Optional[int]

    def __str__(self):
        return F"""
\tChromosome: {self.chromosome}
\tStart: {self.start_position}
\tDeleted: {self.deleted}
\tReplaced: {self.replaced}"""
