# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import pytest

import spack.environment as ev
import spack.main
from spack.spec import Spec
from spack.version import GitVersion

manager = spack.main.SpackCommand("manager")


@pytest.mark.skip("test is having issues with compiler detection need to fix later")
def test_version_replacement_preserves_all_but_version(tmpdir, do_not_check_runtimes_on_reuse):
    with tmpdir.as_cwd():
        env = ev.create_in_dir(tmpdir.strpath)
        with env:
            env.add("cmake@master~ncurses")
            assert list(env.roots())
            env.concretize()
            manager("pin")

            specs = env.all_specs()
            assert specs
            new_spec_str = specs[0]
            assert "cmake" in new_spec_str
            assert "git." in new_spec_str
            assert "=master" in new_spec_str
            assert "~ncurses" in new_spec_str
