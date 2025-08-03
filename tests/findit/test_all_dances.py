"""Master test file for all FindIt dance functions.

This file imports and runs all publisher-specific dance tests.
"""

# Import all publisher test modules
from .test_aaas import TestAAASTest
from .test_bentham import TestBenthamEurekaSelect
from .test_cambridge import TestCambridgeDance
from .test_jama import TestJAMADance
from .test_jci import TestJCIDance
from .test_jstage import TestJStageDance
from .test_liebert import TestLiebertDance
from .test_lww import TestLWWDance
from .test_mdpi import TestMDPIDance
from .test_nature import TestNatureDance
from .test_pmc import TestPMCTwist
from .test_sage import TestSageDance
from .test_scielo import TestScieloDance
from .test_wolterskluwer import TestWoltersKluwerDance

# This file serves as a central point to run all dance tests
# You can run specific publisher tests individually or all together