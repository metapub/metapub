from .utils import load_journals_from_file


# Elsevier / ScienceDirect is mostly paywalled, unfortunately.
sciencedirect_url = 'http://www.sciencedirect.com/science/article/pii/{piit}'
sciencedirect_journals = load_journals_from_file("sciencedirect")


# Karger: mostly paywalled, but sometimes...
# http://www.karger.com/Article/Pdf/351538
#
# {kid} comes from the final nonzero numbers of the article's DOI.
karger_format = 'http://www.karger.com/Article/Pdf/{kid}'

karger_journals = load_journals_from_file("karger")

# Springer 

springer_journals = load_journals_from_file("springer")

# Wiley 

wiley_journals = load_journals_from_file("wiley")

