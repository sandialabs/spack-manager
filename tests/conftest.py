# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.


import os
from importlib import reload

import pytest

import spack.extensions
from spack.test.conftest import *  # noqa: F401 F403

spack.extensions.get_module("manager")

import spack.extensions.manager as manager  # noqa E402

_test_root = os.path.dirname(__file__)


@pytest.fixture
def mock_manager_config_path():
    """
    Setup to use a testing project repo embedded in the tests, then reset to default when finished
    """
    config_path = os.path.join(_test_root, "mock", "mock_config.yaml")
    manager.config_path = config_path
    manager.__init__()
    yield
    manager.config_path = manager._default_config_path
    manager.__init__()


@pytest.fixture
def on_moonlight(monkeypatch, mock_manager_config_path):
    monkeypatch.setenv("MOONLIGHT", "1")
