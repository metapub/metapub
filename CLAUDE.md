# CLAUDE.md

This file provides coding guidelines for Claude when working on the metapub project.

## Model Selection
1. **Never use Opus** - Always use Sonnet or Haiku models for this project.

## Import Guidelines
2. **Avoid in-function imports** - Place imports at the module level unless ABSOLUTELY necessary to avoid circular import problems. In-function imports should be a last resort and well-documented when used.

## Exception Handling
3. **Avoid huge try-except blocks** - Keep exception handling focused and specific to the operations that might fail.

4. **Don't catch generic exceptions** - Avoid `except Exception:` or bare `except:` blocks. Let programming errors (like AttributeError, TypeError, etc.) bubble up naturally. Only catch specific exceptions you can meaningfully handle.

5. **Let programming errors surface** - Don't suppress bugs by catching them generically. Better to fail fast and fix the underlying issue.

6. **Avoid defensive coding** - When information should be there because it's under our control, the lack of that information should break the code.  The contents of PubMedArticle isn't under our control, so we test and cover missing data gracefully so that code doesn't break.  The results of a web URL get/post attempt aren't under our control, so we DO anticipate specific breaking conditions we know about, but avoid blanket exception-catching.

## Control Flow
7. **Avoid long if-else trees** - Use early returns, guard clauses, or dictionaries/switch patterns instead of deeply nested if-else chains. Prefer clear, linear code flow.

## Branching

**Always start a new branch before making any changes — code, documentation, configuration, or CLAUDE.md itself.** Never commit directly to master. Create a descriptive branch name, do the work, then open a PR.

## Releasing
- Use `/release <version>` for the full release procedure with caveats and checks
- Quick reference: `rm -rf dist/ && .venv/bin/python -m build && twine upload --repository metapub dist/*`
- Version must be bumped in both `metapub/__init__.py` and `setup.py`
- **Always create a GitHub tag and release** after uploading to PyPI:
  ```
  git tag v{version} {version-bump-commit-sha}
  git push origin v{version}
  gh release create v{version} --title "v{version}" --notes "..."
  ```

## FindIt / Publisher Dance Tests

**Failing findit tests are a signal, not a nuisance.** When a dance function test fails, the first question is always: *is the publisher's site/format still the same?*

- **Do not mock away a failing test without first confirming the underlying code still works.** If a test like `test_dovepress_waltz_*` fails because `the_dovepress_peacock` can't find a PDF link, that means the publisher changed their HTML — the function is broken for real users, and making the test pass with a mock just hides that.

- **A passing test that uses a synthetic mock is not evidence the code works.** It's evidence the mock works.

- **When a live findit test fails, the correct responses are (in order of preference):**
  1. Investigate the current publisher HTML/behavior and fix the dance function to handle the new format
  2. If the publisher is temporarily down or behind bot-protection, mark the test `@pytest.mark.skip` with an explanation
  3. If the functionality is permanently gone, delete the test and document why in the dance function

- **The correct use of mocks in dance tests** is to test parsing logic against *real saved HTML* (like the PubMed XML fixture approach in `tests/fixtures/pmid_xml/`). If you need to mock an HTTP call, the mock response content should be actual HTML sourced from the publisher site, not synthetic HTML you invented.

- **Wrong mock target is a legitimate bug.** If a test patches `requests.get` but the code uses `requests.Session.get`, fixing the mock target is correct — that's a test bug. This is different from mocking to hide broken functionality.

## CI vs Live Network Tests

The test suite is split into two categories:

**Offline tests (run in CI on every push/PR):**
- Mocked HTTP calls, saved XML/HTML fixtures, logic-only tests
- Run with: `pytest -m "not live_network"` (~625 tests, ~5 min)
- These should always pass. A failure here is a real bug in our code.

**Live network tests (run manually, for drift detection):**
- Make real HTTP requests to publisher websites
- Marked with `@pytest.mark.live_network`
- Run with: `pytest -m live_network` (~52 tests)
- These are **intentionally kept** — they are the early-warning system for publisher format changes. When one fails, it means a publisher changed something and the dance function needs updating.

**The philosophy:**
- Live network tests exist to detect *drift* (publishers changing their HTML, adding bot protection, etc.), not to test our code logic. Our code logic is tested by the offline suite.
- Use `@pytest.mark.live_network` **sparingly** — only on tests that actually hit publisher websites, not NCBI/eutils calls.
- Never convert a failing live test into a passing mocked test without first fixing the underlying code. That turns a drift detector into a dead sensor.
- Live tests should be run by a human who can interpret the results: "did we break something, or did the publisher change something?"

## Additional Guidelines
- Follow the existing code patterns and conventions in the metapub codebase
- Maintain the current architecture and design patterns
- Write clear, focused functions with single responsibilities
