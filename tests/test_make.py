# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import pytest

import spack.environment as ev
import spack.extensions
import spack.extensions.manager.manager_cmds.develop as m_develop
import spack.main

env = spack.main.SpackCommand("env")
manager = spack.main.SpackCommand("manager")
add = spack.main.SpackCommand("add")


@pytest.mark.usefixtures("mutable_mock_env_path_wh_manager", "mock_packages", "mock_fetch")
def test_spackManagerMakeRequiresDevelopSpec():
    env("create", "test")
    with ev.read("test"):
        add("mpich")
        with pytest.raises(spack.main.SpackCommandError) as error:
            out = manager("make", "mpich")
            assert "must be a develop spec" in str(out)
