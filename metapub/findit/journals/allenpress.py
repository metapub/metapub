"""
Allen Press journal list.

Allen Press is a scholarly publishing services company that partners with
scholarly and professional societies to publish their journals and books.
They provide publishing services for journals in medicine, science, education,
and other academic fields.

URL format: https://meridian.allenpress.com/[journal-code]/article-pdf/{doi}
Alternative: https://meridian.allenpress.com/[journal-code]/article/{doi}

DOI patterns: Various (depends on the society/journal)
"""

# Allen Press journals from meridian.allenpress.com cluster (39 journals)
allenpress_journals = []  # Journal list moved to YAML configuration

# Allen Press URL format - will need to determine specific journal codes
allenpress_format = 'https://meridian.allenpress.com/{journal_code}/article-pdf/{doi}'