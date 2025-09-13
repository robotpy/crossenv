#
# To run the tests, you must have crossenv installed and the following environment
# variables must be set:
#
#   CROSSENV_TEST_BUILD_PYTHON=/path/to/build/python3.x
#   CROSSENV_TEST_HOST_PYTHON=/path/to/target/python3.x
#   CROSSENV_TEST_ARCH=arch system machine
#
# The crossenv testing docker images already have these environment variables set.
#

import pytest

from . import testutils

from .resources import host_python, build_python, architecture


@pytest.fixture(scope="module")
def crossenv(tmp_path_factory, host_python, build_python):
    """Convenience fixture for a per-module crossenv with default
    parameters."""
    tmp = tmp_path_factory.mktemp("crossenv")
    return testutils.make_crossenv(tmp, host_python, build_python)
