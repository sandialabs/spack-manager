import os
import pytest

import spack.repo
from spack.spec import Spec
from spack.test.conftest import *  # noqa: F401


@pytest.fixture(scope='session')
def builtin_repo_path():
    yield os.path.join(os.environ['SPACK_MANAGER'], 'spack', 'var', 'spack', 'repos', 'builtin')

@pytest.fixture(scope='session')
def exawind_repo_path():
    yield os.path.join(os.environ['SPACK_MANAGER'], 'repos', 'exawind')

@pytest.fixture(scope='session')
def create_package(builtin_repo_path, exawind_repo_path):
    packages = {}

    def _create(spec):
        if spec not in packages:
            packages[spec] = _create_new(spec)
        return packages[spec]

    def _create_new(spec):
        with spack.repo.use_repositories(builtin_repo_path, exawind_repo_path):
            return Spec(spec).package

    return _create
