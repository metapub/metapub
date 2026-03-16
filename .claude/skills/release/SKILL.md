---
name: release
description: Release a new version of metapub to PyPI. Use when the user wants to cut a release.
argument-hint: <version>
disable-model-invocation: true
---

# Metapub Release Process

Release metapub version `$ARGUMENTS` to PyPI. Follow every step in order.

## Pre-release checklist

1. Ensure you are on the `master` branch with a clean working tree:
   ```
   git checkout master && git pull
   git status
   ```
2. Verify all intended changes are merged. Review recent commits:
   ```
   git log --oneline -10
   ```

## Version bump

Update the version string in **both** of these files:
- `metapub/__init__.py` — `__version__ = '<version>'`
- `setup.py` — `version="<version>"`

Commit and push the version bump directly to master:
```
git add metapub/__init__.py setup.py
git commit -m "Bump version to <version>"
git push
```

## Build

Always clean old artifacts before building:
```
rm -rf dist/
.venv/bin/python -m build
```

### Verify metadata version

After building, check that the wheel has `Metadata-Version: 2.1` (not 2.4):
```
unzip -p dist/metapub-<version>-py2.py3-none-any.whl metapub-<version>.dist-info/METADATA | head -5
```

If you see `Metadata-Version: 2.4`, the build used a setuptools >= 75 which produces
`License-File` fields that twine rejects. Fix by ensuring `pyproject.toml` pins
`setuptools>=40.8.0,<75` in `[build-system] requires`, then rebuild.

## Upload to PyPI

```
twine upload --repository metapub dist/*
```

- This uses the `metapub` repository entry in `~/.pypirc`.
- If twine reports `InvalidDistribution: ... unrecognized or malformed field 'license-file'`,
  the metadata version is wrong — go back to the build step and check the setuptools pin.

## Post-release

1. Verify the release is live: `https://pypi.org/project/metapub/<version>/`
2. Comment on any issues that were fixed in this release with:
   "Fixed in PR #NNN. Will be released in <version>."
   (Or if already released: "Released in <version>.")

## Known caveats

### setuptools metadata compatibility
- `pyproject.toml` pins `setuptools>=40.8.0,<75` to avoid Metadata-Version 2.4.
- setuptools 75+ introduced Metadata 2.4 which adds `License-File` fields.
- twine (both 5.x and 6.x) rejects these fields during upload.
- This pin will need revisiting when twine adds 2.4 support — tracked upstream.

### Build isolation
- `python -m build` creates an **isolated environment**, so the setuptools version
  in your .venv does not matter — only the pin in `pyproject.toml` controls it.

### PyPI repository config
- Upload uses `--repository metapub` which maps to a `[metapub]` section in `~/.pypirc`.
- Do not use `--repository pypi` or the default — it may point to the wrong index.

### Two version locations
- Version must be updated in both `metapub/__init__.py` and `setup.py`.
- These must always match. There is no single-source-of-truth mechanism yet (see #93
  for the setup.py modernization issue).
