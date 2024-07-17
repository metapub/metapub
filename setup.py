import glob
import os

from setuptools import setup, find_packages

setup(
    name='metapub',
    version='0.5.12',
    description='Pubmed / NCBI / eutils interaction library, handling the metadata of pubmed papers.',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    url='https://github.com/metapub/metapub',
    author='Naomi Most',
    maintainer='Naomi Most',
    author_email='naomi@nthmost.com',
    maintainer_email='naomi@nthmost.com',
    license='Apache 2.0',
    packages=find_packages(),
    entry_points={'console_scripts': [
        'pubmed_article = metapub.pubmedfetcher_cli:main',
        'convert = metapub.convert:main',
    ]
    },
    extras_require={
        'test': [
            'tox',
            'pytest',
        ],
    },
    install_requires=[
        'setuptools',
        'lxml',
        'lxml_html_clean',
        'requests',
        'eutils',
        'habanero',
        'tabulate',
        'cssselect',
        'unidecode',
        'docopt',
        'six',
        'coloredlogs',
        'python-Levenshtein',
    ],
)
