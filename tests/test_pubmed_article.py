import unittest
from metapub.exceptions import *
from metapub import PubMedArticle, PubMedFetcher

import random

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
        self.fetch = PubMedFetcher()

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
