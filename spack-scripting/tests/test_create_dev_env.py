import os
from unittest.mock import patch

import manager_cmds.create_dev_env
import pytest

import spack.main

manager = spack.main.SpackCommand('manager')


def test_allSpecsCallSpackDevelop(tmpdir):
	with tmpdir.as_cwd():
		with patch("manager_cmds.create_dev_env.develop") as mock_dev:
			manager('create-dev-env', '-s', 'amr-wind@main',
			        'nalu-wind@master', 'exawind@master')
		mock_dev.assert_any_call('amr-wind@main')
		mock_dev.assert_any_call('nalu-wind@master')
		mock_dev.assert_any_call('exawind@master')


def test_newEnvironmentIsCreated(tmpdir):
	with tmpdir.as_cwd():
		with patch("manager_cmds.create_dev_env.develop") as mock_dev:
			manager('create-dev-env', '-s', 'amr-wind@main',
			        'nalu-wind@master', 'exawind@master')
		assert os.path.isfile(tmpdir.join('spack.yaml'))
		assert os.path.isfile(tmpdir.join('include.yaml'))
