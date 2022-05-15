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


class PackageMap:
    def __init__(self, *paths):
        self.paths = paths
        self.packages = {}

    def create(self, spec):
        if spec not in self.packages:
            self.packages[spec] = self._create_new(spec)
        return self.packages[spec]

    def _create_new(self, spec):
        with spack.repo.use_repositories(*self.paths):
            return Spec(spec).package

@pytest.fixture(scope='session')
def packages(builtin_repo_path, exawind_repo_path):
    return PackageMap(builtin_repo_path, exawind_repo_path)
