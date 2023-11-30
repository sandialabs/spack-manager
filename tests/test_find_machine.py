# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import pytest

import spack.main

mgrCmd = spack.main.SpackCommand("manager")


def test_find_machine_detects_project_machines(mock_manager_config_path):
    out = mgrCmd("find-machine", "--list")
    assert "moonlight" in out


def test_find_machineFindsExpectedMachine(mock_manager_config_path):
    out = mgrCmd("find-machine")
    assert "moonlight" not in out
    os.environ["MOONLIGHT"] = "1"
    out = mgrCmd("find-machine")
    assert "moonlight" in out
