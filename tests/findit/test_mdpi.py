"""Tests for MDPI (Multidisciplinary Digital Publishing Institute) dance function."""

from .common import BaseDanceTest
from metapub import FindIt


class TestMDPIDance(BaseDanceTest):
    """Test cases for MDPI (Multidisciplinary Digital Publishing Institute)."""

    def test_mdpi_moonwalk(self):
        """Test MDPI moonwalk dance function for backup PDF access."""
        # Test MDPI journals that use the_mdpi_moonwalk for backup access
        
        # Membranes journal - known MDPI publication
        pmid_membranes = '38786952'  # 2024 - DOI: 10.3390/membranes14050101
        source = FindIt(pmid=pmid_membranes)
        assert source.pma.journal == 'Membranes (Basel)'
        assert source.pma.doi == '10.3390/membranes14050101'
        # MDPI should work via PMC primarily, but moonwalk backup available
        assert source.url is not None
        # Should get PMC URL as primary source
        assert "europepmc.org" in source.url
        
    def test_mdpi_moonwalk_backup(self):
        """Test MDPI moonwalk dance function generates correct backup URLs."""
        from metapub.findit.dances import the_mdpi_moonwalk
        from metapub import PubMedFetcher
        
        # Test the moonwalk function directly to verify backup URL generation
        pmfetch = PubMedFetcher()
        pma = pmfetch.article_by_pmid('38786952')  # Membranes article
        
        # Test moonwalk without verification to check URL construction
        backup_url = the_mdpi_moonwalk(pma, verify=False)
        
        # Should generate backup PDF URL by appending /pdf to resolved DOI
        assert backup_url == 'https://www.mdpi.com/2077-0375/14/5/101/pdf'
        assert backup_url.endswith('/pdf')
        assert 'mdpi.com' in backup_url
        
        # Test with different MDPI journal
        pma2 = pmfetch.article_by_pmid('38804339')  # Methods Protoc
        backup_url2 = the_mdpi_moonwalk(pma2, verify=False)
        assert backup_url2 == 'https://www.mdpi.com/2409-9279/7/3/45/pdf'
        assert backup_url2.endswith('/pdf')
        assert 'mdpi.com' in backup_url2