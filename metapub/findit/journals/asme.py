"""
ASME (American Society of Mechanical Engineers) journal list.

ASME is a professional engineering society that publishes technical journals
covering mechanical engineering, biomechanical engineering, manufacturing,
energy, and related fields. Their journals are hosted on the ASME Digital
Collection platform.

URL format: https://asmedigitalcollection.asme.org/[journal]/article-pdf/{doi}
Alternative: https://asmedigitalcollection.asme.org/[journal]/article/{doi}

DOI patterns: Typically 10.1115/* for ASME journals
"""

# ASME journals from asmedigitalcollection.asme.org cluster (39 journals)
asme_journals = []  # Journal list moved to YAML configuration

# ASME URL format - will need to determine journal codes
asme_format = 'https://asmedigitalcollection.asme.org/{journal_code}/article-pdf/{doi}'
asme_template = asme_format  # Alias for test compatibility