import os
from pathlib import Path
from collections import namedtuple

import pytest

from .testutils import Resource

Architecture = namedtuple("Architecture", "name system machine")


@pytest.fixture(scope="session")
def architecture():
    name, system, machine = os.environ["CROSSENV_TEST_ARCH"].split()
    return Architecture(name, system, machine)


@pytest.fixture(scope="session")
def build_python():
    path = Path(os.environ["CROSSENV_TEST_BUILD_PYTHON"])
    return Resource(path)


class EmulatedResource(Resource):
    def __init__(self, binary: Path, arch: Architecture):
        super().__init__(binary)
        self.arch = arch

    def _popen(self, func, *args, **kwargs):
        if args[0][0] == self.binary:
            args = ([f"qemu-{self.arch.machine}"] + args[0], *args[1:])

        return super()._popen(func, *args, **kwargs)


@pytest.fixture(scope="session")
def host_python(architecture):
    path = Path(os.environ["CROSSENV_TEST_HOST_PYTHON"])
    return EmulatedResource(path, architecture)
