# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import spack.main

manager = spack.main.SpackCommand("manager")


def testCreateMachineSpecificIncludesFile(on_moonlight, tmpdir):
    with tmpdir.as_cwd():
        assert not os.path.isfile("include.yaml")
        manager("include")
        assert os.path.isfile("include.yaml")


def testCustomIncludeName(on_moonlight, tmpdir):
    with tmpdir.as_cwd():
        assert not os.path.isfile("custom.yaml")
        manager("include", "--file", "custom.yaml")
        assert os.path.isfile("custom.yaml")


def testUserSelectedMachine(mock_manager_config_path, tmpdir):
    with tmpdir.as_cwd():
        assert not os.path.isfile("include.yaml")
        manager("include", "--machine", "moonlight")
        assert os.path.isfile("include.yaml")
