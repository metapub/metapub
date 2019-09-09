from __future__ import absolute_import, print_function, unicode_literals

from metapub import FindIt

from config import JOURNAL_LIST_FILENAME, JOURNAL_ISOABBR_LIST_FILENAME

def parse_journal_chunk(chunk):
    '''Takes a text "chunk" containing Journal information from the NCBI
    Entrez.txt list of journals in pubmed.

    Returns a dictionary containing parsed info about the Journal.
    '''
    #JrId: 44       <-- Entrez Journal ID
    #JournalTitle: Acta chirurgica Italica   <-- sometimes colons appear in name
    #MedAbbr: Acta Chir Ital        <-- MedLine abbreviation of journal title
    #ISSN (Print): 0001-5466
    #ISSN (Online): 
    #IsoAbbr: Acta Chir Ital        <-- ISO (Entrez) abbreviation of journal title
    #NlmId: 0370303     <-- NLM Journal ID

    return dict([line.strip().split(':', 1) for line in chunk.strip().split('\n')])

def parse_journal_blob(blob):
    '''Takes the text content of the JOURNAL_LIST_URL response and
    parses it into a list of chunks that can be parsed by 
    parse_journal_entry.

    :param: blob (string)
    :return: list of chunks
    '''

    chunks = blob.split('--------------------------------------------------------')
    return chunks

def get_jdicts(chunks):
    jdicts = []
    for chunk in chunks:
        if chunk.strip():
            jdicts.append(parse_journal_chunk(chunk.strip()))
    return jdicts

def get_journal_chunks(jlist_filename):
    chunks = []
    with open(jlist_filename) as fh:
        chunks = parse_journal_blob(fh.read())
    return chunks

def main(jlist_filename=JOURNAL_LIST_FILENAME):
    chunks = get_journal_chunks(jlist_filename)
    jdicts = get_jdicts(chunks)

    fout = open(JOURNAL_ISOABBR_LIST_FILENAME, 'w')
    for jdict in jdicts:
        fout.write(jdict['IsoAbbr'].strip() + '\n')

    print()
    print('[Done] %i journal names written to %s' % (len(jdicts), JOURNAL_ISOABBR_LIST_FILENAME))

if __name__=='__main__':
    main()

