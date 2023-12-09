# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.


import os

import pytest

import spack.extensions.manager as manager
from spack.test.conftest import *  # noqa: F401 F403

_test_root = os.path.dirname(__file__)

# mocking fixture idea taken from 
# https://stackoverflow.com/questions/28716832/how-to-test-function-is-called-with-correct-arguments-with-pytest/28719648#28719648
@pytest.fixture
def argtest():
    class TestArgs(object):
        def __init__(self):
            self.args = []
        @property
        def num_calls(self):
            return len(self.args)
        def __call__(self, *args): 
            self.args.extend(list(args))
    return TestArgs()

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
