"""DEPRECATED: FindIt dance tests have been refactored.

This file has been refactored into publisher-specific test files in tests/findit/.

New structure:
- tests/findit/test_aaas.py - AAAS (Science) journals
- tests/findit/test_bentham.py - Bentham Science Publishers
- tests/findit/test_cambridge.py - Cambridge University Press
- tests/findit/test_jama.py - JAMA network
- tests/findit/test_jci.py - Journal of Clinical Investigation
- tests/findit/test_jstage.py - J-STAGE journals
- tests/findit/test_liebert.py - Mary Ann Liebert Publishers
- tests/findit/test_lww.py - LWW platform
- tests/findit/test_mdpi.py - MDPI
- tests/findit/test_nature.py - Nature Publishing Group
- tests/findit/test_pmc.py - PMC access
- tests/findit/test_sage.py - SAGE Publications
- tests/findit/test_scielo.py - SciELO
- tests/findit/test_wolterskluwer.py - Wolters Kluwer

To run all dance tests: pytest tests/findit/
To run specific publisher tests: pytest tests/findit/test_[publisher].py
"""

import warnings
warnings.warn(
    "test_findit_dances.py is deprecated. Use tests/findit/test_[publisher].py instead.",
    DeprecationWarning,
    stacklevel=2
)