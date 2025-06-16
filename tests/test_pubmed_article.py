import unittest
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
