# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.


import os
import pytest

import spack.paths
import spack.repo
from spack.spec import Spec
from spack.test.conftest import *  # noqa: F401


@pytest.fixture(scope='session')
def builtin_repo_path():
    yield spack.paths.packages_path

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
