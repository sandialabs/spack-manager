# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import spack.extensions.manager as manager
import spack.extensions.manager.manager_cmds.find_machine as find_machine
import spack.main

mgr_cmd = spack.main.SpackCommand("manager")


def test_find_machine_detects_project_machines(mock_manager_config_path):
    assert manager.config_path != manager._default_config_path
    assert find_machine.machine_defined("moonlight")
    out = mgr_cmd("find-machine", "--list")
    assert "moonlight" in out


def test_find_machine_finds_expected_machine(mock_manager_config_path):
    assert manager.config_path != manager._default_config_path
    out = mgr_cmd("find-machine")
    assert "moonlight" not in out
    os.environ["MOONLIGHT"] = "1"
    out = mgr_cmd("find-machine")
    assert "moonlight" in out


def test_find_machine_filters_on_project(mock_manager_config_path):
    out = mgr_cmd("find-machine", "--project", "project_a", "--list")
    assert "moonlight" in out
    out = mgr_cmd("find-machine", "--project", "project_b", "--list")
    assert "moonlight" not in out


def test_find_machine_config_points_to_path(mock_manager_config_path):
    assert manager.config_path != manager._default_config_path
    assert find_machine.machine_defined("moonlight")
    out = mgr_cmd("find-machine", "--config")
    assert "moonlight" in out
    assert os.path.isdir(out)
