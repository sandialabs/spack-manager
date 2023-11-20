# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import pytest

import spack.main

mgrCmd = spack.main.SpackCommand("manager")

def test_find_machine_detects_project_machines(mock_manager_config_path):
    out = mgrCmd("find-machine", "--list")
    assert "moonlight" in out

