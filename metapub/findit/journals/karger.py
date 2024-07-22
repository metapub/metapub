from .utils import load_journals_from_file

# karger: mostly paywalled, but sometimes...
# http://www.karger.com/Article/Pdf/351538
#
# {kid} comes from the final nonzero numbers of the article's DOI.
karger_format = 'http://www.karger.com/Article/Pdf/{kid}'

karger_journals = load_journals_from_file("karger")

