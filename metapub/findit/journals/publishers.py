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

# Wolters Kluwer
#
# Some of this stuff is Free and/or Open Access.
#
# http://journals.lww.com/pain/Fulltext/2015/07000/Social_communication_model_of_pain.7.aspx

wolterskluwer_journals = load_journals_from_file("wolterskluwer")

