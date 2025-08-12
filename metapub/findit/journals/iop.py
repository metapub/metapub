"""
IOP Publishing (Institute of Physics Publishing) journal list.

IOP Publishing (formerly Institute of Physics Publishing) is a British publisher
focused on physics and related fields. They publish journals through both
iopscience.iop.org and validate.perfdrive.com domains.

URL format: https://iopscience.iop.org/article/{doi}/pdf
Alternative formats: https://validate.perfdrive.com/article/{doi}/pdf

DOI patterns: various (10.1088/* is most common for IOP)
"""

# Combined IOP journals from both validate.perfdrive.com and iopscience.iop.org clusters
iop_journals = []  # Journal list moved to YAML configuration

# IOP uses multiple URL formats
iop_format = 'https://iopscience.iop.org/article/{doi}/pdf'
iop_alt_format = 'https://validate.perfdrive.com/article/{doi}/pdf'