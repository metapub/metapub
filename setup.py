import glob
import os
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop


def rebuild_journal_registry():
    """Rebuild the journal registry database after installation."""
    try:
        import subprocess
        import sys
        from pathlib import Path
        
        # Find the registry builder script  
        package_root = Path(__file__).parent
        registry_script = package_root / 'metapub' / 'scripts' / 'build_registry_from_yaml.py'
        
        if not registry_script.exists():
            raise FileNotFoundError(f"Registry builder script not found at {registry_script}")
        
        print("Rebuilding journal registry from YAML configuration...")
        
        # Run the registry builder
        result = subprocess.run([
            sys.executable, str(registry_script),
            '--yaml-dir', str(package_root / 'metapub' / 'findit' / 'journals_yaml' / 'publishers'),
            '--output-db', str(package_root / 'metapub' / 'findit' / 'data' / 'registry.db')
        ], capture_output=True, text=True, cwd=str(package_root))
        
        if result.returncode == 0:
            print("Journal registry rebuilt successfully!")
            if result.stdout:
                print(result.stdout.strip())
        else:
            raise RuntimeError(f"Registry build failed: {result.stderr}")
            
    except Exception as e:
        print(f"Warning: Could not rebuild journal registry: {e}")
        print("You can manually rebuild it later with: python scripts/build_registry_from_yaml.py")


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
    version="0.6.4",
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
            "metapub_build_registry = metapub.scripts.build_registry_from_yaml:main",
            "metapub-registry = metapub.findit.cli:main",
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
        "pyyaml",
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
