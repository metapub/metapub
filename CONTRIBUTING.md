# Contributing to Metapub

This document is for contributors and maintainers working on `metapub` itself. Created
by Codex.

## Setup

### Repo setup

1. Clone the repository, create a virtual environment, and install the project in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[test]"
```

An editable install will automatically rebuild the FindIt journal registry during installation.

### API keys

Metapub works best with an NCBI API key.

1. Create an account using CMU Single Sign On at <https://www.ncbi.nlm.nih.gov/myncbi/>
2. Retrieve an API key from <https://account.ncbi.nlm.nih.gov/settings/>
3. Export the API key before running metapub:

```bash
export NCBI_API_KEY="your_key_here"
```

You do not strictly need an API key, but without one NCBI rate limits are lower.

## Development

Create a feature branch before making changes. Do not work directly on `master`.

If you want to check NCBI availability first:

```bash
ncbi_health_check --quick && pytest tests/
```

The journal registry database needs to be rebuilt when making changes to the YAML configuration files. The registry is automatically rebuilt during installation, but you can also rebuild it manually using:

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

## Testing
Run the test suite with:

```bash
pytest tests/
```

To force network tests even when the health check would skip them:

```bash
FORCE_NETWORK_TESTS=1 pytest tests/
```
