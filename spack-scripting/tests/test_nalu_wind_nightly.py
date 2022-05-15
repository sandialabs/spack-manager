import os
import pytest

import spack.repo
from spack.spec import Spec


def test_can_read_exawind_repo(exawind_repo_path, builtin_repo_path):
    assert os.path.isdir(exawind_repo_path)
    assert os.path.isdir(builtin_repo_path)
    with spack.repo.use_repositories(exawind_repo_path, builtin_repo_path) as exawind_repo:
        abstract_spec = Spec('nalu-wind-nightly')
        concrete_spec = abstract_spec.concretize()
        assert concrete_spec.variants('extra_name')
        package = concrete_spec.package
        package.ctest_args()
        assert package.spec.variants['extra_name'] != 'default'
