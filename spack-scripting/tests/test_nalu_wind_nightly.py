import os
import pytest

import spack.repo
from spack.spec import Spec


def test_can_read_exawind_repo(exawind_repo_path, builtin_repo_path):
    assert os.path.isdir(exawind_repo_path)
    assert os.path.isdir(builtin_repo_path)
    with spack.repo.use_repositories(exawind_repo_path, builtin_repo_path) as exawind_repo:
        spec = Spec('nalu-wind-nightly')
        spec.concretize()
        assert spec.variants['extra_name'].value == 'default'
        package = spec.package
        #package.ctest_args()  # test chokes on setting CMAKE_CXX_COMPILER from mpi spec ...
        assert package.spec.variants['extra_name'].value == 'default'
