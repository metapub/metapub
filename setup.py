import glob
import os
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop


def rebuild_journal_registry():
    """Rebuild the journal registry database after installation."""
    try:
        # Import here to avoid circular imports during setup
        from metapub.findit.migrate_journals import migrate_journals
        print("Rebuilding journal registry...")
        stats = migrate_journals()
        print(f"Journal registry rebuilt: {stats}")
    except Exception as e:
        print(f"Warning: Could not rebuild journal registry: {e}")
        print("You can manually rebuild it later with: metapub_migrate_journals --force")


class PostInstallCommand(install):
    """Custom install command that rebuilds the journal registry."""

    def run(self):
        install.run(self)
        self.execute(rebuild_journal_registry, [], msg="Rebuilding journal registry...")


class PostDevelopCommand(develop):
    """Custom develop command that rebuilds the journal registry."""

    def run(self):
        develop.run(self)
        self.execute(rebuild_journal_registry, [], msg="Rebuilding journal registry...")


setup(
    name="metapub",
    version="0.6.4a",
    description="Pubmed / NCBI / eutils interaction library, handling the metadata of pubmed papers.",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    url="https://metapub.org",
    author="Naomi Most",
    maintainer="Naomi Most",
    author_email="naomi@nthmost.com",
    maintainer_email="naomi@nthmost.com",
    license="Apache 2.0",
    packages=find_packages(),
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
    entry_points={
        "console_scripts": [
            "pubmed_article = metapub.pubmedfetcher_cli:main",
            "convert = metapub.convert:main",
            "ncbi_health_check = metapub.ncbi_health_check:main",
            "metapub_migrate_journals = metapub.findit.migrate_journals:main",
        ]
    },
    # Include all Python files in the package
    include_package_data=True,
    extras_require={
        "test": [
            "tox",
            "pytest",
        ],
    },
    install_requires=[
        "setuptools",
        "lxml",
        "lxml_html_clean",
        "requests",
        "eutils",
        "habanero",
        "tabulate",
        "cssselect",
        "unidecode",
        "docopt",
        "six",
        "coloredlogs",
        "python-Levenshtein",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
)
