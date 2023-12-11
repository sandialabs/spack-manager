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


class Patcher(object):
    """
    Class to capture arguments, and potentially patch the behavior of any attribute
    to be paired with monkeypatch.setattr
    # mocking fixture idea taken from
    # https://stackoverflow.com/questions/28716832/how-to-test-function-is-called-with-correct-arguments-with-pytest/28719648#28719648
    """

    def __init__(self, patch_func=None):
        self.args = []
        self.patch_func = patch_func

    @property
    def num_calls(self):
        return len(self.args)

    def __call__(self, *args):
        self.args.extend(list(args))
        if self.patch_func:
            self.patch_func(*args)

    def assert_any_call(self, call_args):
        assert call_args in self.args

    def assert_call_matches(self, call_index, call_args):
        assert call_index <= self.num_calls
        assert call_args == self.args[call_index]


@pytest.fixture
def arg_capture():
    """
    Fixture to capture arguments each time a patched
    function is called.
    Needs to be used in conjuction
    with monkeypatch.setattr
    """
    return Patcher()


@pytest.fixture
def arg_capture_patch():
    """
    Fixture to record arguments each time called
    and patch behavior
    Needs to be used in conjuction
    with monkeypatch.setattr
    """

    def _patch(patch_func=None):
        return Patcher(patch_func)

    return _patch


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


@pytest.fixture
def mutable_mock_env_path_wh_manager(mutable_mock_env_path, mutable_config):
    mutable_config.set("config:extensions", [os.path.join(__file__, "..", "..")])
