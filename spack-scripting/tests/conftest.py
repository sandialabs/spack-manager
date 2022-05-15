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
    def create(spec):
        with spack.repo.use_repositories(exawind_repo_path, builtin_repo_path) as exawind_repo:
            spec = Spec('nalu-wind-nightly')
            spec.concretize()
            return spec.package

    return create
