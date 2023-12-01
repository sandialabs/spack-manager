# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.


import os

import manager
import pytest

from spack.test.conftest import *  # noqa: F401 F403

_test_root = os.path.dirname(__file__)


@pytest.fixture
def mock_manager_config_path(monkeypatch):
    """ "Setup to use a testing project repo embedded in the tests"""
    print(_test_root)
    config_path = os.path.join(_test_root, "mock", "mock_config.yaml")
    print("CONFIG PATH:", config_path, os.path.isfile(config_path))
    monkeypatch.setattr(
        manager, "config_path", config_path
    )
    print("MOCK CONFIG PATH:", manager.config_path, os.path.isfile(manager.config_path))
    manager.populate_config()
    manager.load_projects()


@pytest.fixture
def on_moonlight(monkeypatch, mock_manager_config_path):
    monkeypatch.setenv("MOONLIGHT", "1")
    print(os.environ)
