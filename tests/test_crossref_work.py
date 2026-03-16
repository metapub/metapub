import unittest

from metapub.crossref import CrossRefWork


class TestCrossRefWorkNoneAuthor(unittest.TestCase):
    """Test that CrossRefWork handles None/missing author data gracefully."""

    def setUp(self):
        self.work = CrossRefWork(
            DOI='10.1234/test',
            title=['Test Title'],
            author=None,
            container_title=['Test Journal'],
            issued={'date-parts': [[2024]]},
        )

    def test_author_list_returns_empty_list(self):
        self.assertEqual(self.work.author_list, [])

    def test_author_list_last_fm_returns_empty_list(self):
        self.assertEqual(self.work.author_list_last_fm, [])

    def test_author1_returns_empty_string(self):
        self.assertEqual(self.work.author1, '')

    def test_author1_last_fm_returns_empty_string(self):
        self.assertEqual(self.work.author1_last_fm, '')

    def test_authors_str_lastfirst_returns_empty_string(self):
        self.assertEqual(self.work.authors_str_lastfirst, '')

    def test_to_citation_returns_dict(self):
        cit = self.work.to_citation()
        self.assertIsInstance(cit, dict)
        self.assertEqual(cit['aulast'], '')
        self.assertEqual(cit['authors'], [])

    def test_citation_property(self):
        # Should not crash
        result = self.work.citation
        self.assertIsInstance(result, str)


class TestCrossRefWorkIncompleteAuthor(unittest.TestCase):
    """Test that CrossRefWork handles author dicts missing 'given' key."""

    def setUp(self):
        self.work = CrossRefWork(
            DOI='10.1234/test2',
            title=['Test Title 2'],
            author=[
                {'sequence': 'first', 'family': 'Smith'},
                {'sequence': 'additional', 'name': 'Some Consortium'},
            ],
            container_title=['Test Journal'],
            issued={'date-parts': [[2024]]},
        )

    def test_author_list(self):
        self.assertEqual(self.work.author_list, ['Smith', 'Some Consortium'])

    def test_author_list_last_fm(self):
        self.assertEqual(self.work.author_list_last_fm, ['Smith', 'Some Consortium'])

    def test_author1(self):
        self.assertEqual(self.work.author1, 'Smith')

    def test_author1_last_fm(self):
        self.assertEqual(self.work.author1_last_fm, 'Smith')

    def test_authors_str_lastfirst(self):
        self.assertEqual(self.work.authors_str_lastfirst, 'Smith;Some Consortium')


class TestCrossRefWorkNormalAuthor(unittest.TestCase):
    """Verify normal author data still works correctly."""

    def setUp(self):
        self.work = CrossRefWork(
            DOI='10.1234/test3',
            title=['Test Title 3'],
            author=[
                {'sequence': 'first', 'given': 'John', 'family': 'Doe'},
                {'sequence': 'additional', 'given': 'Jane', 'family': 'Smith'},
            ],
            container_title=['Test Journal'],
            issued={'date-parts': [[2024]]},
        )

    def test_author_list(self):
        self.assertEqual(self.work.author_list, ['John Doe', 'Jane Smith'])

    def test_author_list_last_fm(self):
        self.assertEqual(self.work.author_list_last_fm, ['Doe J', 'Smith J'])

    def test_author1(self):
        self.assertEqual(self.work.author1, 'John Doe')

    def test_to_citation(self):
        cit = self.work.to_citation()
        self.assertEqual(cit['aulast'], 'Doe')
        self.assertEqual(cit['authors'], ['Doe J', 'Smith J'])
