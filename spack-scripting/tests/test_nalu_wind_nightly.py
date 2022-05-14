import pytest

import spack.repo
from spack.spec import Spec


def test_can_read_exawind_repo(exawind_repo_path):
    with spack.repo.use_repositories(exawind_repo_path) as exawind_repo:
        concrete_spec = Spec('nalu-wind-nightly').concretize()
