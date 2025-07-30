import unittest
from datetime import datetime
from metapub.cache_utils import cleanup_dir
from metapub.exceptions import *
from metapub import PubMedArticle, PubMedFetcher

import random

from tests.common import TEST_CACHEDIR

xml_str1 = '''<?xml version="1.0"?>
<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2015//EN" "http://www.ncbi.nlm.nih.gov/corehtml/query/DTD/pubmed_150101.dtd">
<PubmedArticleSet>
<PubmedArticle>
    <MedlineCitation Owner="NLM" Status="MEDLINE">
        <PMID Version="1">4</PMID>
        <DateCreated>
            <Year>1976</Year>
            <Month>01</Month>
            <Day>10</Day>
        </DateCreated>
        <DateCompleted>
            <Year>1976</Year>
            <Month>01</Month>
            <Day>10</Day>
        </DateCompleted>
        <DateRevised>
            <Year>2013</Year>
            <Month>11</Month>
            <Day>21</Day>
        </DateRevised>
        <Article PubModel="Print">
            <Journal>
                <ISSN IssnType="Print">0006-291X</ISSN>
                <JournalIssue CitedMedium="Print">
                    <Volume>66</Volume>
                    <Issue>4</Issue>
                    <PubDate>
                        <Year>1975</Year>
                        <Month>Oct</Month>
                        <Day>27</Day>
                    </PubDate>
                </JournalIssue>
                <Title>Biochemical and biophysical research communications</Title>
                <ISOAbbreviation>Biochem. Biophys. Res. Commun.</ISOAbbreviation>
            </Journal>
            <ArticleTitle>Effect of chloroquine on cultured fibroblasts: release of lysosomal hydrolases and inhibition of their uptake.</ArticleTitle>
            <Pagination>
                <MedlinePgn>1338-43</MedlinePgn>
            </Pagination>
            <AuthorList CompleteYN="Y">
                <Author ValidYN="Y">
                    <LastName>Wiesmann</LastName>
                    <ForeName>U N</ForeName>
                    <Initials>UN</Initials>
                </Author>
                <Author ValidYN="Y">
                    <LastName>DiDonato</LastName>
                    <ForeName>S</ForeName>
                    <Initials>S</Initials>
                </Author>
                <Author ValidYN="Y">
                    <LastName>Herschkowitz</LastName>
                    <ForeName>N N</ForeName>
                    <Initials>NN</Initials>
                </Author>
            </AuthorList>
            <Language>eng</Language>
            <PublicationTypeList>
                <PublicationType UI="D016428">Journal Article</PublicationType>
            </PublicationTypeList>
        </Article>
        <MedlineJournalInfo>
            <Country>UNITED STATES</Country>
            <MedlineTA>Biochem Biophys Res Commun</MedlineTA>
            <NlmUniqueID>0372516</NlmUniqueID>
            <ISSNLinking>0006-291X</ISSNLinking>
        </MedlineJournalInfo>
        <ChemicalList>
            <Chemical>
                <RegistryNumber>886U3H6UFF</RegistryNumber>
                <NameOfSubstance UI="D002738">Chloroquine</NameOfSubstance>
            </Chemical>
            <Chemical>
                <RegistryNumber>EC 3.1.6.-</RegistryNumber>
                <NameOfSubstance UI="D013429">Sulfatases</NameOfSubstance>
            </Chemical>
            <Chemical>
                <RegistryNumber>EC 3.1.6.8</RegistryNumber>
                <NameOfSubstance UI="D002553">Cerebroside-Sulfatase</NameOfSubstance>
            </Chemical>
            <Chemical>
                <RegistryNumber>EC 3.2.1.31</RegistryNumber>
                <NameOfSubstance UI="D005966">Glucuronidase</NameOfSubstance>
            </Chemical>
            <Chemical>
                <RegistryNumber>K3R6ZDH4DU</RegistryNumber>
                <NameOfSubstance UI="D003911">Dextrans</NameOfSubstance>
            </Chemical>
        </ChemicalList>
        <CitationSubset>IM</CitationSubset>
        <MeshHeadingList>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D001692">Biological Transport</DescriptorName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D002478">Cells, Cultured</DescriptorName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D002553">Cerebroside-Sulfatase</DescriptorName>
                <QualifierName MajorTopicYN="Y" UI="Q000378">metabolism</QualifierName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D002738">Chloroquine</DescriptorName>
                <QualifierName MajorTopicYN="Y" UI="Q000494">pharmacology</QualifierName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D003911">Dextrans</DescriptorName>
                <QualifierName MajorTopicYN="N" UI="Q000378">metabolism</QualifierName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D005347">Fibroblasts</DescriptorName>
                <QualifierName MajorTopicYN="N" UI="Q000201">enzymology</QualifierName>
                <QualifierName MajorTopicYN="N" UI="Q000378">metabolism</QualifierName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D005966">Glucuronidase</DescriptorName>
                <QualifierName MajorTopicYN="Y" UI="Q000378">metabolism</QualifierName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D006801">Humans</DescriptorName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D007966">Leukodystrophy, Metachromatic</DescriptorName>
                <QualifierName MajorTopicYN="N" UI="Q000201">enzymology</QualifierName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D008247">Lysosomes</DescriptorName>
                <QualifierName MajorTopicYN="N" UI="Q000187">drug effects</QualifierName>
                <QualifierName MajorTopicYN="Y" UI="Q000201">enzymology</QualifierName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D010873">Pinocytosis</DescriptorName>
                <QualifierName MajorTopicYN="N" UI="Q000187">drug effects</QualifierName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D012867">Skin</DescriptorName>
                <QualifierName MajorTopicYN="N" UI="Q000201">enzymology</QualifierName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName MajorTopicYN="N" UI="D013429">Sulfatases</DescriptorName>
                <QualifierName MajorTopicYN="Y" UI="Q000378">metabolism</QualifierName>
            </MeshHeading>
        </MeshHeadingList>
    </MedlineCitation>
    <PubmedData>
        <History>
            <PubMedPubDate PubStatus="pubmed">
                <Year>1975</Year>
                <Month>10</Month>
                <Day>27</Day>
            </PubMedPubDate>
            <PubMedPubDate PubStatus="medline">
                <Year>1975</Year>
                <Month>10</Month>
                <Day>27</Day>
                <Hour>0</Hour>
                <Minute>1</Minute>
            </PubMedPubDate>
            <PubMedPubDate PubStatus="entrez">
                <Year>1975</Year>
                <Month>10</Month>
                <Day>27</Day>
                <Hour>0</Hour>
                <Minute>0</Minute>
            </PubMedPubDate>
        </History>
        <PublicationStatus>ppublish</PublicationStatus>
        <ArticleIdList>
            <ArticleId IdType="pubmed">4</ArticleId>
            <ArticleId IdType="pii">0006-291X(75)90506-9</ArticleId>
        </ArticleIdList>
    </PubmedData>
</PubmedArticle>

</PubmedArticleSet>
'''

xml_str2 = '''
    <MedlineCitation Owner="NLM" Status="MEDLINE">
        <PMID Version="1">23697015</PMID>
        <DateCreated>
            <Year>2013</Year>
            <Month>05</Month>
            <Day>23</Day>
        </DateCreated>
        <DateCompleted>
            <Year>2013</Year>
            <Month>07</Month>
            <Day>11</Day>
        </DateCompleted>
        <Article PubModel="Print">
        <Journal>
            <ISSN IssnType="Print">1110-0583</ISSN>
            <JournalIssue CitedMedium="Print">
                <Volume>43</Volume>
                <Issue>1</Issue>
                <PubDate>
                    <Year>2013</Year>
                    <Month>Apr</Month>
                </PubDate>
            </JournalIssue>
            <Title>Journal of the Egyptian Society of Parasitology</Title>
            <ISOAbbreviation>J Egypt Soc Parasitol</ISOAbbreviation>
        </Journal>
        <ArticleTitle>The Rift Valley fever: could re-emerge in Egypt again?</ArticleTitle>
        <Pagination>
            <MedlinePgn>41-56</MedlinePgn>
        </Pagination>
        <Abstract>
            <AbstractText>The Rift Valley fever (RVF) is a neglected, emerging, mosquito-borne disease with severe negative impact on human and animal health and economy. RVF is caused by RVF virus of the family of Bunyaviridae, genus Phlebovirus. RVF is an acute, febrile disease affecting humans and a wide range of animals. The virus is trans-mitted through the bites from mosquitoes and exposure to viremic blood, body fluids, or contact with tissues of infected animals or by inhaling natural virus aerosols, also possibly by consumption of infected unpasteurized milk. The RVF-virus replicate at the site introduction and in local lymphatic followed by viremia and spread to other organs as the liver and central nervous system, causing the hepatic necrosis and eosinophilia cytoplasmic degeneration. The main signs and symptoms are fever, headache, myalgia, arthralgia, photophobia, bradycardia, conjunctivitis and flushing face. Main complications include jaundice, hemorrhagic, meningoencephalitis and retinal lesions. Generally speaking, in the 21st Century, the vector-borne infectious diseases, was accepted as the disaster issues with the considerable significant morbidity and mortality. These facts should be considered by the public health, veterinary and agricultural authorities</AbstractText>
        </Abstract>
        <AuthorList CompleteYN="Y">
            <Author ValidYN="Y">
                <LastName>El-Bahnasawy</LastName>
                <ForeName>Mamdouh</ForeName>
                <Initials>M</Initials>
                <Affiliation>The Military Medical Services For Preventive Medicine, Ain Shams University, Cairo 11566, Egypt.</Affiliation>
            </Author>
            <Author ValidYN="Y">
                <LastName>Megahed</LastName>
                <ForeName>Laila Abdel-Mawla</ForeName>
                <Initials>LA</Initials>
            </Author>
            <Author ValidYN="Y">
                <LastName>Abdalla Saleh</LastName>
                <ForeName>Hala Ahmed</ForeName>
                <Initials>HA</Initials>
            </Author>
            <Author ValidYN="Y">
                <LastName>Morsy</LastName>
                <ForeName>Tosson A</ForeName>
                <Initials>TA</Initials>
            </Author>
        </AuthorList>
        <Language>eng</Language>
        <PublicationTypeList>
            <PublicationType>Journal Article</PublicationType>
        </PublicationTypeList>
    </Article>
    <MedlineJournalInfo>
        <Country>Egypt</Country>
        <MedlineTA>J Egypt Soc Parasitol</MedlineTA>
        <NlmUniqueID>8102141</NlmUniqueID>
        <ISSNLinking>1110-0583</ISSNLinking>
    </MedlineJournalInfo>
    <CitationSubset>IM</CitationSubset>
    <MeshHeadingList>
        <MeshHeading>
            <DescriptorName MajorTopicYN="N">Animals</DescriptorName>
        </MeshHeading>
        <MeshHeading>
            <DescriptorName MajorTopicYN="N">Communicable Diseases, Emerging</DescriptorName>
            <QualifierName MajorTopicYN="Y">epidemiology</QualifierName>
        </MeshHeading>
        <MeshHeading>
            <DescriptorName MajorTopicYN="N">Culicidae</DescriptorName>
        </MeshHeading>
        <MeshHeading>
            <DescriptorName MajorTopicYN="N" Type="Geographic">Egypt</DescriptorName>
            <QualifierName MajorTopicYN="N">epidemiology</QualifierName>
        </MeshHeading>
        <MeshHeading>
            <DescriptorName MajorTopicYN="N">Humans</DescriptorName>
        </MeshHeading>
        <MeshHeading>
            <DescriptorName MajorTopicYN="N">Insect Vectors</DescriptorName>
        </MeshHeading>
        <MeshHeading>
            <DescriptorName MajorTopicYN="N">Phlebovirus</DescriptorName>
        </MeshHeading>
        <MeshHeading>
            <DescriptorName MajorTopicYN="N">Rift Valley Fever</DescriptorName>
            <QualifierName MajorTopicYN="Y">epidemiology</QualifierName>
        </MeshHeading>
        <MeshHeading>
            <DescriptorName MajorTopicYN="N" Type="Geographic">Saudi Arabia</DescriptorName>
            <QualifierName MajorTopicYN="N">epidemiology</QualifierName>
        </MeshHeading>
        <MeshHeading>
            <DescriptorName MajorTopicYN="N" Type="Geographic">Sudan</DescriptorName>
            <QualifierName MajorTopicYN="N">epidemiology</QualifierName>
        </MeshHeading>
    </MeshHeadingList>
</MedlineCitation>
'''


class TestPubMedArticle(unittest.TestCase):

    def setUp(self):
        self.fetch = PubMedFetcher(cachedir=TEST_CACHEDIR)

    def tearDown(self):
        pass

    def test_random_efetch(self):
        pmid = str(random.randint(22222222, 23333333))
        try:
            article = self.fetch.article_by_pmid(pmid)
            if article is not None:
                assert article.pmid == pmid
                assert article.title is not None
        except InvalidPMID:
            self.test_random_efetch()
            # print "PMID %s returned InvalidPMID response (which is totally OK). Run test again!" % pmid

    def test_init1(self):
        """
        Test on the xml returned by eutils
        """
        article = PubMedArticle(xml_str1)
        assert str(article.pmid) == '4'

    def test_init2(self):
        """
        Test on the xml downloaded from medline
        """
        article = PubMedArticle(xml_str2)
        assert str(article.pmid) == '23697015'

    def test_to_dict(self):
        article = PubMedArticle(xml_str1)
        self.assertTrue(isinstance(article.to_dict(), dict))

    def test_embedded_xml_tags(self):
        """
        Some articles have xml tags embedded in their title or abstract.
        Example: "Exploring the effect of vitamin D<sub>3</sub> supplementation"
        Naive parsing with elem.text will truncate the contents at the first tag.
        Instead, we want to keep the whole contents, including any embedded XML tags.
        """
        with open('tests/data/pmid_28731372.xml') as f:
            xml = f.read()
        article = PubMedArticle(xml)
        expected_title = 'Exploring the effect of vitamin D<sub>3</sub> supplementation ' \
        'on the anti-EBV antibody response in relapsing-remitting multiple sclerosis.'
        self.assertEqual(article.title, expected_title)
        abstract = article.abstract
        expected_objectives = 'OBJECTIVES: To investigate the effect of high-dose vitamin D<sub>3</sub> supplements'
        self.assertTrue(expected_objectives in abstract)
        expected_conclusion = 'CONCLUSION: High-dose vitamin D<sub>3</sub> supplementation selectively reduces anti-EBNA-1 antibody levels'
        self.assertTrue(expected_conclusion in abstract)
        self.assertTrue(abstract.startswith('BACKGROUND: Epstein-Barr virus (EBV) infection and vitamin D insufficiency'))
        self.assertTrue(abstract.endswith('do not implicate a promoted immune response against EBV as the underlying mechanism.'))

    def test_mesh_heading_parsing_detailed(self):
        """
        Tests the parsing of MeSH headings, specifically checking the new structure
        with a list of qualifiers and their major topic statuses, using PMID 34558640.
        """
        pmid = "34558640"
        article = self.fetch.article_by_pmid(pmid)
        self.assertIsNotNone(article, f"Failed to fetch article for PMID {pmid}")

        mesh_data = article.mesh
        # Based on the provided XML for PMID 34558640:
        # <MeshHeadingList>
        #     <MeshHeading>
        #         <DescriptorName UI="D000072224" MajorTopicYN="N">Bcl-2-Like Protein 11</DescriptorName>
        #         <QualifierName UI="Q000235" MajorTopicYN="N">genetics</QualifierName>
        #     </MeshHeading>
        #     <MeshHeading>
        #         <DescriptorName UI="D002289" MajorTopicYN="N">Carcinoma, Non-Small-Cell Lung</DescriptorName>
        #         <QualifierName UI="Q000188" MajorTopicYN="Y">drug therapy</QualifierName>
        #         <QualifierName UI="Q000235" MajorTopicYN="N">genetics</QualifierName>
        #         <QualifierName UI="Q000473" MajorTopicYN="N">pathology</QualifierName>
        #     </MeshHeading>
        #     <MeshHeading>
        #         <DescriptorName UI="D019008" MajorTopicYN="N">Drug Resistance, Neoplasm</DescriptorName>
        #     </MeshHeading>
        #     <MeshHeading>
        #         <DescriptorName UI="D066246" MajorTopicYN="N">ErbB Receptors</DescriptorName>
        #         <QualifierName UI="Q000037" MajorTopicYN="Y">antagonists & inhibitors</QualifierName>
        #         <QualifierName UI="Q000235" MajorTopicYN="N">genetics</QualifierName>
        #         <QualifierName UI="Q000502" MajorTopicYN="N">physiology</QualifierName>
        #     </MeshHeading>
        # ... and others
        # </MeshHeadingList>

        self.assertIn("D002289", mesh_data, "Descriptor D002289 not found in MeSH data.")
        d002289 = mesh_data["D002289"]
        self.assertEqual(d002289['descriptor_name'], 'Carcinoma, Non-Small-Cell Lung')
        self.assertFalse(d002289['descriptor_major_topic'])
        self.assertEqual(len(d002289['qualifiers']), 3)

        # Check qualifiers for D002289
        expected_qual_d002289_dt = {'qualifier_name': 'drug therapy', 'qualifier_ui': 'Q000188', 'qualifier_major_topic': True}
        expected_qual_d002289_ge = {'qualifier_name': 'genetics', 'qualifier_ui': 'Q000235', 'qualifier_major_topic': False}
        expected_qual_d002289_pa = {'qualifier_name': 'pathology', 'qualifier_ui': 'Q000473', 'qualifier_major_topic': False}

        self.assertIn(expected_qual_d002289_dt, d002289['qualifiers'])
        self.assertIn(expected_qual_d002289_ge, d002289['qualifiers'])
        self.assertIn(expected_qual_d002289_pa, d002289['qualifiers'])

        self.assertIn("D019008", mesh_data, "Descriptor D019008 not found in MeSH data.")
        d019008 = mesh_data["D019008"]
        self.assertEqual(d019008['descriptor_name'], 'Drug Resistance, Neoplasm')
        self.assertFalse(d019008['descriptor_major_topic'])
        self.assertEqual(len(d019008['qualifiers']), 0, "D019008 should have no qualifiers.")

        self.assertIn("D066246", mesh_data, "Descriptor D066246 not found in MeSH data.")
        d066246 = mesh_data["D066246"]
        self.assertEqual(d066246['descriptor_name'], 'ErbB Receptors')
        self.assertFalse(d066246['descriptor_major_topic'])
        self.assertEqual(len(d066246['qualifiers']), 3)

        # Check qualifiers for D066246
        expected_qual_d066246_ai = {'qualifier_name': 'antagonists & inhibitors', 'qualifier_ui': 'Q000037', 'qualifier_major_topic': True}
        expected_qual_d066246_ge = {'qualifier_name': 'genetics', 'qualifier_ui': 'Q000235', 'qualifier_major_topic': False}
        expected_qual_d066246_ph = {'qualifier_name': 'physiology', 'qualifier_ui': 'Q000502', 'qualifier_major_topic': False}

        self.assertIn(expected_qual_d066246_ai, d066246['qualifiers'])
        self.assertIn(expected_qual_d066246_ge, d066246['qualifiers'])
        self.assertIn(expected_qual_d066246_ph, d066246['qualifiers'])

        # Check D000072224
        self.assertIn("D000072224", mesh_data, "Descriptor D000072224 not found in MeSH data.")
        d000072224 = mesh_data["D000072224"]
        self.assertEqual(d000072224['descriptor_name'], 'Bcl-2-Like Protein 11')
        self.assertFalse(d000072224['descriptor_major_topic'])
        self.assertEqual(len(d000072224['qualifiers']), 1)
        expected_qual_d000072224_ge = {'qualifier_name': 'genetics', 'qualifier_ui': 'Q000235', 'qualifier_major_topic': False}
        self.assertIn(expected_qual_d000072224_ge, d000072224['qualifiers'])

    def test_pubdate_property_comprehensive(self):
        """
        Test the pubdate property across different eras and edge cases with real PMIDs.
        This protects against regressions in publication date extraction.
        """
        from datetime import datetime
        
        # Test cases covering different eras and scenarios including non-English
        test_cases = [
            # Very early PubMed (1970s)
            {"pmid": "1000", "expected_year": 1975, "description": "1975 early PubMed record"},
            {"pmid": "100000", "expected_year": 1978, "description": "1978 article"},
            
            # 1980s
            {"pmid": "500000", "expected_year": 1979, "description": "1979 article"},
            {"pmid": "3000000", "expected_year": 1985, "description": "1985 article"},
            
            # 1990s era
            {"pmid": "7518611", "expected_year": 1994, "description": "1994 article"},
            {"pmid": "9562523", "expected_year": 1997, "description": "1997 article"},
            
            # 2000s era  
            {"pmid": "10440612", "expected_year": 1999, "description": "1999 article"},
            {"pmid": "15764155", "expected_year": 2005, "description": "2005 article"},
            {"pmid": "18393105", "expected_year": 2008, "description": "2008 article"},
            
            # 2010s era
            {"pmid": "20095872", "expected_year": 2010, "description": "2010 article"},
            {"pmid": "23985001", "expected_year": 2013, "description": "2013 article"},
            {"pmid": "25532429", "expected_year": 2015, "description": "2015 article"},
            
            # 2020s era
            {"pmid": "34889398", "expected_year": 2021, "description": "2021 recent article"},
            
            # Known edge cases
            {"pmid": "7550356", "expected_year": 1995, "description": "Zero authors edge case"},
            
            # Book example (GeneReviews)
            {"pmid": "20301546", "expected_year": 2006, "description": "Book chapter"},
            
            # Non-English articles
            {"pmid": "31671389", "expected_year": 2019, "description": "Spanish article"},
            {"pmid": "36890755", "expected_year": 2023, "description": "Japanese article"},
            {"pmid": "1234567", "expected_year": 1975, "description": "German historical article"},
        ]
        
        for case in test_cases:
            with self.subTest(pmid=case["pmid"], description=case["description"]):
                try:
                    article = self.fetch.article_by_pmid(case["pmid"])
                    
                    # Test that pubdate property exists and returns datetime
                    self.assertIsNotNone(article.pubdate, 
                        f"PMID {case['pmid']}: pubdate should not be None")
                    self.assertIsInstance(article.pubdate, datetime,
                        f"PMID {case['pmid']}: pubdate should be datetime object")
                    
                    # Test year matches expected
                    self.assertEqual(article.pubdate.year, case["expected_year"],
                        f"PMID {case['pmid']}: expected year {case['expected_year']}, got {article.pubdate.year}")
                    
                    # Test that pubdate year matches year string (when available)
                    if article.year:
                        year_int = int(article.year)
                        self.assertEqual(article.pubdate.year, year_int,
                            f"PMID {case['pmid']}: pubdate year {article.pubdate.year} should match year string {year_int}")
                    
                except Exception as e:
                    self.fail(f"PMID {case['pmid']} ({case['description']}) failed: {e}")

    def test_essential_attributes_protection(self):
        """
        Test that essential PubMedArticle attributes are always present and properly typed
        across different types of articles and eras.
        """
        # Sample PMIDs covering different scenarios
        test_pmids = [
            "1000",      # 1975 - very early
            "7518611",   # 1994 - pre-digital era  
            "18393105",  # 2008 - modern era
            "34889398",  # 2021 - recent
            "20301546",  # Book chapter (GeneReviews)
        ]
        
        # Essential attributes that should always be present
        essential_attrs = {
            'pmid': str,
            'url': str, 
            'title': (str, type(None)),
            'authors': list,
            'author_list': list,
            'authors_str': str,
            'year': (str, int, type(None)),  # Can be str or int depending on source
            'journal': (str, type(None)),
            'abstract': (str, type(None)),
            'keywords': list,
            'history': dict,
            'pubmed_type': str,
            'pubdate': (datetime, type(None)),  # Our new property
            'grants': list,  # Actually shared between articles and books
            'publication_types': dict,  # Also shared between articles and books
        }
        
        # Article-only attributes
        article_only_attrs = {
            'volume': (str, type(None)),
            'issue': (str, type(None)), 
            'pages': (str, type(None)),
            'first_page': (str, type(None)),
            'last_page': (str, type(None)),
            'volume_issue': (str, type(None)),
            'doi': (str, type(None)),
            'pii': (str, type(None)),
            'pmc': (str, type(None)),
            'issn': (str, type(None)),
            'mesh': (dict, type(None)),
            'chemicals': (dict, type(None)),
        }
        
        # Book-only attributes  
        book_only_attrs = {
            'book_accession_id': (str, type(None)),
            'book_title': (str, type(None)),
            'book_publisher': (str, type(None)),
            'book_language': (str, type(None)),
            'book_editors': (list, type(None)),
            'book_abstracts': (dict, type(None)),
            'book_sections': (dict, type(None)),
            'book_copyright': (str, type(None)),
            'book_medium': (str, type(None)),
            'book_synonyms': (list, type(None)),
            'book_publication_status': (str, type(None)),
            'book_history': (dict, type(None)),
            'book_contribution_date': (datetime, type(None)),
            'book_date_revised': (datetime, type(None)),
        }
        
        for pmid in test_pmids:
            with self.subTest(pmid=pmid):
                try:
                    article = self.fetch.article_by_pmid(pmid)
                    
                    # Test essential attributes
                    for attr_name, expected_type in essential_attrs.items():
                        self.assertTrue(hasattr(article, attr_name),
                            f"PMID {pmid}: Missing essential attribute '{attr_name}'")
                        
                        attr_value = getattr(article, attr_name)
                        if isinstance(expected_type, tuple):
                            self.assertIsInstance(attr_value, expected_type,
                                f"PMID {pmid}: Attribute '{attr_name}' should be {expected_type}, got {type(attr_value)}")
                        else:
                            self.assertIsInstance(attr_value, expected_type,
                                f"PMID {pmid}: Attribute '{attr_name}' should be {expected_type}, got {type(attr_value)}")
                    
                    # Test type-specific attributes
                    if article.pubmed_type == 'article':
                        # Articles should have these attributes (can be None)
                        for attr_name, expected_type in article_only_attrs.items():
                            self.assertTrue(hasattr(article, attr_name),
                                f"PMID {pmid}: Missing article attribute '{attr_name}'")
                            
                            attr_value = getattr(article, attr_name)
                            if isinstance(expected_type, tuple):
                                self.assertIsInstance(attr_value, expected_type,
                                    f"PMID {pmid}: Article attribute '{attr_name}' should be {expected_type}, got {type(attr_value)}")
                            
                        # Book attributes should be None for articles
                        for attr_name in book_only_attrs.keys():
                            if hasattr(article, attr_name):
                                attr_value = getattr(article, attr_name)
                                self.assertIsNone(attr_value,
                                    f"PMID {pmid}: Article should have book attribute '{attr_name}' as None, got {attr_value}")
                    
                    elif article.pubmed_type == 'book':
                        # Books should have book attributes
                        for attr_name, expected_type in book_only_attrs.items():
                            self.assertTrue(hasattr(article, attr_name),
                                f"PMID {pmid}: Missing book attribute '{attr_name}'")
                                
                        # Article-only attributes should be None for books
                        for attr_name in article_only_attrs.keys():
                            if hasattr(article, attr_name):
                                attr_value = getattr(article, attr_name)
                                self.assertIsNone(attr_value,
                                    f"PMID {pmid}: Book should have article attribute '{attr_name}' as None, got {attr_value}")
                    
                except Exception as e:
                    self.fail(f"PMID {pmid} attribute protection test failed: {e}")

    def test_medlinedate_parsing_edge_cases(self):
        """
        Test MedlineDate parsing with various edge case formats that appear in real data.
        """
        from xml.etree.ElementTree import Element, SubElement
        
        # Create a test article to access _parse_medlinedate method
        test_article = self.fetch.article_by_pmid('1000')
        
        # Test cases for MedlineDate parsing
        medlinedate_cases = [
            # Standard cases
            {"input": "2007 Spring", "expected_year": 2007, "expected_month": 3},
            {"input": "2007 Mar-Apr", "expected_year": 2007, "expected_month": 3},
            {"input": "1999-2000", "expected_year": 1999, "expected_month": 1},
            {"input": "2007 Sep 15-30", "expected_year": 2007, "expected_month": 9},
            {"input": "Fall 2006", "expected_year": 2006, "expected_month": 9},
            {"input": "Winter 2005", "expected_year": 2005, "expected_month": 12},
            
            # Edge cases mentioned in code comments
            {"input": "2007 (details online)", "expected_year": 2007, "expected_month": 1},
            
            # Year only
            {"input": "2007", "expected_year": 2007, "expected_month": 1},
            {"input": "1995", "expected_year": 1995, "expected_month": 1},
            
            # Month variations
            {"input": "2007 December", "expected_year": 2007, "expected_month": 12},
            {"input": "2007 Dec", "expected_year": 2007, "expected_month": 12},
            {"input": "Jan 2008", "expected_year": 2008, "expected_month": 1},
            
            # Invalid/empty cases
            {"input": "", "expected_result": None},
            {"input": "Invalid Date", "expected_result": None},
            {"input": "Spring only", "expected_result": None},
        ]
        
        for case in medlinedate_cases:
            with self.subTest(medlinedate=case["input"]):
                result = test_article._parse_medlinedate(case["input"])
                
                if "expected_result" in case and case["expected_result"] is None:
                    self.assertIsNone(result, f"Expected None for '{case['input']}', got {result}")
                else:
                    self.assertIsNotNone(result, f"Expected datetime for '{case['input']}', got None")
                    self.assertEqual(result.year, case["expected_year"],
                        f"Year mismatch for '{case['input']}': expected {case['expected_year']}, got {result.year}")
                    self.assertEqual(result.month, case["expected_month"],
                        f"Month mismatch for '{case['input']}': expected {case['expected_month']}, got {result.month}")

    def test_citation_properties_comprehensive(self):
        """
        Test that all citation properties work correctly across different article types and eras.
        """
        test_cases = [
            {"pmid": "1000", "description": "1975 early article"},
            {"pmid": "23435529", "description": "Modern article with full metadata"},
            {"pmid": "34889398", "description": "Recent article (2021)"},
            {"pmid": "20301546", "description": "Book chapter (GeneReviews)"},
        ]
        
        for case in test_cases:
            with self.subTest(pmid=case["pmid"], description=case["description"]):
                try:
                    article = self.fetch.article_by_pmid(case["pmid"])
                    
                    # Test citation property
                    citation = article.citation
                    self.assertIsInstance(citation, str)
                    self.assertGreater(len(citation), 10, "Citation should be substantial")
                    
                    # Test citation_html property
                    citation_html = article.citation_html
                    self.assertIsInstance(citation_html, str)
                    self.assertGreater(len(citation_html), 10, "HTML citation should be substantial")
                    
                    # HTML citation should contain HTML tags for formatting
                    if article.pubmed_type == 'article' and article.journal:
                        self.assertIn('<i>', citation_html, "HTML citation should contain italics for journal")
                    
                    # Test citation_bibtex property
                    citation_bibtex = article.citation_bibtex
                    self.assertIsInstance(citation_bibtex, str)
                    self.assertGreater(len(citation_bibtex), 20, "BibTeX citation should be substantial")
                    
                    # BibTeX should start with @article or @book
                    expected_type = '@book' if article.book_accession_id else '@article'
                    self.assertTrue(citation_bibtex.startswith(expected_type),
                        f"BibTeX should start with {expected_type}")
                    
                    # BibTeX should end with }
                    self.assertTrue(citation_bibtex.endswith('}'),
                        "BibTeX should end with closing brace")
                    
                    # BibTeX should contain author field if authors exist
                    if article.authors:
                        self.assertIn('author = {', citation_bibtex, "BibTeX should contain author field")
                    
                    # BibTeX should contain title field if title exists
                    if article.title:
                        self.assertIn('title = {', citation_bibtex, "BibTeX should contain title field")
                    
                    # BibTeX should contain year field if year exists
                    if article.year:
                        self.assertIn('year = {', citation_bibtex, "BibTeX should contain year field")
                    
                except Exception as e:
                    self.fail(f"Citation properties test failed for PMID {case['pmid']}: {e}")

    def test_author_handling_variations(self):
        """
        Test author parsing across different formats and edge cases found in real data.
        """
        test_cases = [
            {"pmid": "1000", "description": "1975 article with standard authors"},
            {"pmid": "7550356", "description": "Article with potential author issues"},
            {"pmid": "34889398", "description": "Modern article with multiple authors"},
        ]
        
        for case in test_cases:
            with self.subTest(pmid=case["pmid"], description=case["description"]):
                try:
                    article = self.fetch.article_by_pmid(case["pmid"])
                    
                    # Test authors attribute
                    self.assertIsInstance(article.authors, list)
                    
                    # Test author_list attribute (PubMedAuthor objects)
                    self.assertIsInstance(article.author_list, list)
                    self.assertEqual(len(article.authors), len(article.author_list),
                        "authors and author_list should have same length")
                    
                    # Test authors_str
                    self.assertIsInstance(article.authors_str, str)
                    
                    # If authors exist, check formatting
                    if article.authors:
                        for author in article.authors:
                            self.assertIsInstance(author, str)
                            # Authors should be in "LastName FirstInitials" format typically
                            self.assertGreater(len(author.strip()), 0, "Author name should not be empty")
                        
                        # authors_str should contain semicolons if multiple authors
                        if len(article.authors) > 1:
                            self.assertIn(';', article.authors_str, 
                                "Multiple authors should be separated by semicolons")
                        
                        # Test first author properties
                        self.assertIsNotNone(article.author1_last_fm)
                        self.assertIsNotNone(article.author1_lastfm)
                        self.assertEqual(article.author1_last_fm.replace(' ', ''), article.author1_lastfm)
                    
                except Exception as e:
                    self.fail(f"Author handling test failed for PMID {case['pmid']}: {e}")

    def test_year_consistency_across_eras(self):
        """
        Test that year extraction is consistent across different PubMed eras and formats.
        """
        era_test_cases = [
            # Each era might have different XML formatting for dates
            {"pmid": "1000", "expected_year": "1975", "era": "1970s"},
            {"pmid": "3000000", "expected_year": "1985", "era": "1980s"},
            {"pmid": "7518611", "expected_year": "1994", "era": "1990s"},
            {"pmid": "15764155", "expected_year": "2005", "era": "2000s"},
            {"pmid": "23985001", "expected_year": "2013", "era": "2010s"},
            {"pmid": "34889398", "expected_year": "2021", "era": "2020s"},
        ]
        
        for case in era_test_cases:
            with self.subTest(pmid=case["pmid"], era=case["era"]):
                try:
                    article = self.fetch.article_by_pmid(case["pmid"])
                    
                    # Test year string extraction
                    self.assertEqual(article.year, case["expected_year"],
                        f"Year string mismatch for {case['era']} article")
                    
                    # Test pubdate year consistency
                    if article.pubdate:
                        self.assertEqual(str(article.pubdate.year), case["expected_year"],
                            f"Pubdate year should match year string for {case['era']} article")
                    
                except Exception as e:
                    self.fail(f"Year consistency test failed for {case['era']} PMID {case['pmid']}: {e}")

    def test_book_vs_article_attribute_isolation(self):
        """
        Test that book and article attributes are properly isolated based on pubmed_type.
        """
        # Test article
        article = self.fetch.article_by_pmid("34889398")  # Known article
        self.assertEqual(article.pubmed_type, 'article')
        
        # Article should have article attributes
        self.assertIsNotNone(article.volume)
        self.assertIsNotNone(article.journal)
        
        # Article should have None for book attributes
        self.assertIsNone(article.book_accession_id)
        self.assertIsNone(article.book_title)
        self.assertIsNone(article.book_publisher)
        
        # Test book
        book = self.fetch.article_by_pmid("20301546")  # Known GeneReviews book
        self.assertEqual(book.pubmed_type, 'book')
        
        # Book should have book attributes
        self.assertIsNotNone(book.book_title)
        self.assertIsNotNone(book.book_contribution_date)
        
        # Book should have None for article-only attributes
        self.assertIsNone(book.volume)
        self.assertIsNone(book.issue)
        self.assertIsNone(book.pages)
        self.assertIsNone(book.doi)

    def test_pubdate_source_hierarchy(self):
        """
        Test that pubdate property uses the correct source hierarchy:
        1. PubDate (Year/Month/Day)
        2. MedlineDate
        3. Book contribution date
        4. History dates
        """
        # This is more of a behavioral test to ensure the hierarchy works
        test_cases = [
            {"pmid": "34889398", "expected_source": "structured", "description": "Modern article with structured date"},
            {"pmid": "20301546", "expected_source": "book", "description": "Book with contribution date"},
        ]
        
        for case in test_cases:
            with self.subTest(pmid=case["pmid"], description=case["description"]):
                try:
                    article = self.fetch.article_by_pmid(case["pmid"])
                    
                    # Should have pubdate
                    self.assertIsNotNone(article.pubdate, f"PMID {case['pmid']} should have pubdate")
                    
                    # Check that the expected source type makes sense
                    if case["expected_source"] == "book":
                        self.assertEqual(article.pubmed_type, 'book')
                        self.assertIsNotNone(article.book_contribution_date)
                    elif case["expected_source"] == "structured":
                        self.assertEqual(article.pubmed_type, 'article')
                        # Should have some form of structured date data
                        self.assertTrue(article.year is not None or article.history)
                    
                except Exception as e:
                    self.fail(f"Pubdate source hierarchy test failed for PMID {case['pmid']}: {e}")

    def test_non_english_articles_comprehensive(self):
        """
        Test that non-English articles are properly handled across all attributes.
        This ensures international language support in PubMedArticle.
        """
        # Non-English PMIDs from various languages
        non_english_pmids = {
            "German": ["39607518", "1234567", "2345678"],
            "French": ["34690539", "3456789", "4567890"],
            "Spanish": ["31671389", "36054861", "6789012"],
            "Italian": ["38880983", "5678901", "8901345"],
            "Japanese": ["36890755", "37743333"],
            "Chinese": ["38468501", "40195673"],
            "Portuguese": ["36043633", "39166619"],
            "Russian": ["36168687", "39731248"]
        }
        
        for language, pmids in non_english_pmids.items():
            for pmid in pmids[:2]:  # Test 2 PMIDs per language to balance thoroughness and speed
                with self.subTest(language=language, pmid=pmid):
                    try:
                        article = self.fetch.article_by_pmid(pmid)
                        
                        # Test essential attributes work for non-English content
                        self.assertIsNotNone(article.pmid, f"{language} PMID {pmid}: pmid should not be None")
                        self.assertIsInstance(article.pmid, str, f"{language} PMID {pmid}: pmid should be string")
                        
                        # Test pubdate property works for non-English articles
                        if article.pubdate:
                            self.assertIsInstance(article.pubdate, datetime,
                                f"{language} PMID {pmid}: pubdate should be datetime object")
                            self.assertGreater(article.pubdate.year, 1900,
                                f"{language} PMID {pmid}: pubdate year should be reasonable")
                        
                        # Test that year extraction works
                        if article.year:
                            year_val = int(article.year) if isinstance(article.year, str) else article.year
                            self.assertGreater(year_val, 1900,
                                f"{language} PMID {pmid}: year should be reasonable")
                        
                        # Test that authors are properly handled (can be empty list)
                        self.assertIsInstance(article.authors, list,
                            f"{language} PMID {pmid}: authors should be list")
                        self.assertIsInstance(article.authors_str, str,
                            f"{language} PMID {pmid}: authors_str should be string")
                        
                        # Test that title handling works (can be None for some articles)
                        if article.title:
                            self.assertIsInstance(article.title, str,
                                f"{language} PMID {pmid}: title should be string when present")
                        
                        # Test that journal handling works
                        if article.journal:
                            self.assertIsInstance(article.journal, str,
                                f"{language} PMID {pmid}: journal should be string when present")
                        
                        # Test that pubmed_type is properly determined
                        self.assertIn(article.pubmed_type, ['article', 'book'],
                            f"{language} PMID {pmid}: pubmed_type should be 'article' or 'book'")
                        
                        # Test that URL generation works
                        self.assertIsInstance(article.url, str,
                            f"{language} PMID {pmid}: URL should be string")
                        self.assertIn(pmid, article.url,
                            f"{language} PMID {pmid}: URL should contain PMID")
                        
                    except Exception as e:
                        self.fail(f"{language} PMID {pmid} failed: {e}")

    def test_non_english_pubdate_property(self):
        """
        Specifically test that the pubdate property works correctly for non-English articles.
        """
        # Representative non-English PMIDs from different languages and eras
        test_cases = [
            {"pmid": "39607518", "language": "German", "expected_min_year": 2020},
            {"pmid": "31671389", "language": "Spanish", "expected_min_year": 2019},
            {"pmid": "36890755", "language": "Japanese", "expected_min_year": 2020},
            {"pmid": "38468501", "language": "Chinese", "expected_min_year": 2020},
            {"pmid": "1234567", "language": "German (historical)", "expected_min_year": 1975},
            {"pmid": "3456789", "language": "French (historical)", "expected_min_year": 1975},
        ]
        
        for case in test_cases:
            with self.subTest(pmid=case["pmid"], language=case["language"]):
                try:
                    article = self.fetch.article_by_pmid(case["pmid"])
                    
                    # Test pubdate property specifically
                    self.assertIsNotNone(article.pubdate,
                        f"{case['language']} PMID {case['pmid']}: pubdate should not be None")
                    self.assertIsInstance(article.pubdate, datetime,
                        f"{case['language']} PMID {case['pmid']}: pubdate should be datetime")
                    
                    # Test year is reasonable
                    self.assertGreaterEqual(article.pubdate.year, case["expected_min_year"],
                        f"{case['language']} PMID {case['pmid']}: pubdate year should be >= {case['expected_min_year']}")
                    
                    # Test consistency with year attribute
                    if article.year:
                        year_val = int(article.year) if isinstance(article.year, str) else article.year
                        self.assertEqual(article.pubdate.year, year_val,
                            f"{case['language']} PMID {case['pmid']}: pubdate year should match year attribute")
                    
                except Exception as e:
                    self.fail(f"{case['language']} PMID {case['pmid']} pubdate test failed: {e}")

    def test_non_english_citation_formatting(self):
        """
        Test that citation formatting works correctly for non-English articles.
        """
        # Test citations for articles from different languages
        test_cases = [
            {"pmid": "31671389", "language": "Spanish"},
            {"pmid": "36890755", "language": "Japanese"},
            {"pmid": "38468501", "language": "Chinese"},
            {"pmid": "1234567", "language": "German (historical)"},
        ]
        
        for case in test_cases:
            with self.subTest(pmid=case["pmid"], language=case["language"]):
                try:
                    article = self.fetch.article_by_pmid(case["pmid"])
                    
                    # Test standard citation
                    citation = article.citation
                    self.assertIsInstance(citation, str,
                        f"{case['language']} PMID {case['pmid']}: citation should be string")
                    self.assertGreater(len(citation), 10,
                        f"{case['language']} PMID {case['pmid']}: citation should be substantial")
                    
                    # Test HTML citation
                    citation_html = article.citation_html
                    self.assertIsInstance(citation_html, str,
                        f"{case['language']} PMID {case['pmid']}: HTML citation should be string")
                    
                    # Test BibTeX citation
                    citation_bibtex = article.citation_bibtex
                    self.assertIsInstance(citation_bibtex, str,
                        f"{case['language']} PMID {case['pmid']}: BibTeX citation should be string")
                    self.assertTrue(citation_bibtex.startswith('@article'),
                        f"{case['language']} PMID {case['pmid']}: BibTeX should start with @article")
                    
                    # BibTeX should have proper structure
                    self.assertTrue(citation_bibtex.endswith('}'),
                        f"{case['language']} PMID {case['pmid']}: BibTeX should end with }}")
                    
                    # Should contain PMID in citation ID or have author-year format
                    self.assertTrue(',' in citation_bibtex,
                        f"{case['language']} PMID {case['pmid']}: BibTeX should have proper format")
                    
                except Exception as e:
                    self.fail(f"{case['language']} PMID {case['pmid']} citation test failed: {e}")

    def test_non_english_character_encoding(self):
        """
        Test that non-ASCII characters in non-English articles are properly handled.
        """
        # PMIDs known to have non-ASCII characters
        test_cases = [
            {"pmid": "31671389", "language": "Spanish", "description": "Spanish characters"},
            {"pmid": "36890755", "language": "Japanese", "description": "Japanese characters"},
            {"pmid": "38468501", "language": "Chinese", "description": "Chinese characters"},
        ]
        
        for case in test_cases:
            with self.subTest(pmid=case["pmid"], language=case["language"]):
                try:
                    article = self.fetch.article_by_pmid(case["pmid"])
                    
                    # Test that title can contain non-ASCII characters
                    if article.title:
                        self.assertIsInstance(article.title, str,
                            f"{case['language']} PMID {case['pmid']}: title should be string")
                        # Should not raise encoding errors when accessed
                        title_len = len(article.title)
                        self.assertGreater(title_len, 0,
                            f"{case['language']} PMID {case['pmid']}: title should have content")
                    
                    # Test that abstract can contain non-ASCII characters
                    if article.abstract:
                        self.assertIsInstance(article.abstract, str,
                            f"{case['language']} PMID {case['pmid']}: abstract should be string")
                    
                    # Test that journal names can contain non-ASCII characters
                    if article.journal:
                        self.assertIsInstance(article.journal, str,
                            f"{case['language']} PMID {case['pmid']}: journal should be string")
                    
                    # Test that author names can contain non-ASCII characters
                    for author in article.authors:
                        self.assertIsInstance(author, str,
                            f"{case['language']} PMID {case['pmid']}: author names should be strings")
                    
                    # Test that citations handle non-ASCII characters properly
                    citation = article.citation
                    self.assertIsInstance(citation, str,
                        f"{case['language']} PMID {case['pmid']}: citation should handle non-ASCII")
                    
                except Exception as e:
                    self.fail(f"{case['language']} PMID {case['pmid']} encoding test failed: {e}")

    def test_multilingual_integration_with_existing_tests(self):
        """
        Add non-English PMIDs to existing comprehensive tests to ensure full coverage.
        """
        # Add some non-English PMIDs to the essential attributes test
        multilingual_test_pmids = [
            "1000",        # English - 1975 (original test case)
            "34889398",    # English - 2021 (original test case)
            "31671389",    # Spanish - 2019
            "36890755",    # Japanese - 2023
            "1234567",     # German - historical
        ]
        
        # Essential attributes that should work regardless of language
        essential_attrs = ['pmid', 'url', 'pubmed_type', 'authors', 'authors_str', 'pubdate']
        
        for pmid in multilingual_test_pmids:
            with self.subTest(pmid=pmid):
                try:
                    article = self.fetch.article_by_pmid(pmid)
                    
                    for attr_name in essential_attrs:
                        self.assertTrue(hasattr(article, attr_name),
                            f"PMID {pmid}: Missing essential attribute '{attr_name}'")
                        
                        attr_value = getattr(article, attr_name)
                        self.assertIsNotNone(attr_value,
                            f"PMID {pmid}: Attribute '{attr_name}' should not be None")
                    
                    # Special test for pubdate across languages
                    if article.pubdate:
                        self.assertIsInstance(article.pubdate, datetime,
                            f"PMID {pmid}: pubdate should be datetime regardless of language")
                        self.assertGreater(article.pubdate.year, 1970,
                            f"PMID {pmid}: pubdate year should be reasonable regardless of language")
                    
                except Exception as e:
                    self.fail(f"Multilingual integration test failed for PMID {pmid}: {e}")
