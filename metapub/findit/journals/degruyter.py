"""
De Gruyter publisher configuration.

Academic publisher with journals across sciences and humanities.
DOI-based PDF access for journals with 10.1515 DOI prefix.

Complete de Gruyter list is here, but not all are in PubMed:
    https://academic.oup.com/journals/pages/journals_a_to_z
"""

# De Gruyter template for DOI-based access
degruyter_template = 'https://www.degruyter.com/document/doi/{doi}/pdf'

degruyter_journals = []  # Journal list moved to YAML configuration
