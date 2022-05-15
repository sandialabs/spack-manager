import os
import pytest

from spack.test.conftest import *  # noqa: F401


@pytest.fixture(scope='session')
def exawind_repo_path():
    yield os.path.join(os.environ['SPACK_MANAGER'], 'repos', 'exawind')

@pytest.fixture(scope='session')
def builtin_repo_path():
    yield os.path.join(os.environ['SPACK_MANAGER'], 'spack', 'var', 'spack', 'repos', 'builtin')
