# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os

import spack.extensions.manager as manager


def test_spackManagerHasConfigPath():
    """Confirm that the manager module is the correct one for populating configs"""
    assert hasattr(manager, "config_path")
    expected_config_path = os.path.realpath(
        os.path.abspath(os.path.join(__file__, "..", "..", "spack-manager.yaml"))
    )
    assert manager.config_path == expected_config_path


def test_defaultConfigIsPopulatedInMemory():
    """Show that the config will always be populated"""
    assert "spack-manager" in manager.config_yaml
    manager_node = manager.config_yaml["spack-manager"]
    assert "projects" in manager_node


def test_mockManagerSoftareProject(mock_manager_config_path):
    """Test verify that we are moking a software project's deployment"""
    assert os.path.isfile(manager.config_path)
    assert "tests" in str(manager.config_path)
    manager_node = manager.config_yaml["spack-manager"]
    projects_node = manager.config_yaml["spack-manager"]["projects"]
    assert "project_a" in projects_node
