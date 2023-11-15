# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import manager


def test_spackManagerHasConfigPath():
    assert hasattr(manager, "config_path")
    expected_config_path = os.path.realpath(
        os.path.abspath(os.path.join(__file__, "..", "..", "spack-manager.yaml"))
    )
    assert manager.config_path == expected_config_path

def test_defaultConfigIsPopulatedInMemory():
    assert "spack-manager" in manager.config_yaml
    manager_node = manager.config_yaml["spack-manager"]
    assert "projects" in manager_node

