# Contributing to Metapub

This document is for contributors and maintainers working on `metapub` itself.

## Maintainer Setup

Clone the repository, create a virtual environment, and install the project in editable mode:

```bash
cd /Users/bgracia/Documents/School/SchoolCode/17780/metapub
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[test]"
```

An editable install will automatically rebuild the FindIt journal registry during installation.

## NCBI Account and API Key

Metapub works best with an NCBI API key.

Maintainer setup notes:

1. Created an account using CMU Single Sign On at <https://www.ncbi.nlm.nih.gov/myncbi/>
2. Fetched API key from <https://account.ncbi.nlm.nih.gov/settings/>
3. Exported the key before running metapub:

```bash
export NCBI_API_KEY="your_key_here"
```

You do not strictly need an API key, but without one NCBI rate limits are lower.

## Development Workflow

Create a feature branch before making changes. Do not work directly on `master`.

Run the test suite with:

```bash
pytest tests/
```

If you want to check NCBI availability first:

```bash
ncbi_health_check --quick && pytest tests/
```

To force network tests even when the health check would skip them:

```bash
FORCE_NETWORK_TESTS=1 pytest tests/
```

## Journal Registry

For developers working on metapub itself, the journal registry database needs to be rebuilt when making changes to the YAML configuration files. The registry is automatically rebuilt during installation, but you can also rebuild it manually using:

```bash
metapub_build_registry
```

This command builds the SQLite registry database from the YAML publisher configuration files located in `metapub/findit/journals_yaml/publishers/`.

You can also pass explicit paths:

```bash
metapub_build_registry --output-db path/to/registry.db --yaml-dir path/to/yaml/files
```

Maintainer notes are available in `README.rst`:
<https://github.com/metapub/metapub/blob/master/README.rst?plain=1#L471>

## Release Notes

Before releasing:

1. Bump the version in `metapub/__init__.py`
2. Bump the version in `setup.py`

Build and upload with:

```bash
python -m pip install build twine
rm -rf dist/
python -m build
twine upload --repository metapub dist/*
```

## Contribution Expectations

If you are fixing a bug or adding a feature:

- Open an issue with enough detail to reproduce the problem when possible
- Include examples of broken input or new data/API behavior
- Add or update tests with the change

For FindIt publisher-specific tests, treat failing live tests as real breakage unless there is a clear reason to skip them temporarily.
