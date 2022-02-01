import os
from unittest.mock import patch

import pytest

import spack.environment as ev
import spack.main

env = spack.main.SpackCommand('env')
manager = spack.main.SpackCommand('manager')


@pytest.mark.usefixtures(
    'mutable_mock_env_path', 'mock_packages', 'mock_fetch')
class TestSpackManagerDevelop(object):
    @patch('manager_cmds.develop.spack_develop.develop')
    def test_spackManagerDevelopCallsSpackDevelop(self, mock_develop):
        env('create', 'test')
        with ev.read('test'):
            manager('develop', 'mpich@1.0')
            mock_develop.assert_called_once()

    @patch('manager_cmds.develop.spack_develop.develop')
    @patch('manager_cmds.develop.git_clone')
    def test_requireUserToSpecifyGitRepoAndBranch(self, mock_git_clone, mock_develop):
        env('create', 'test')
        with ev.read('test') as e:
            branch = 'master'
            repo = 'https://a.git.repo'
            name = 'mpich'
            version = '1.0'
            spec = '{n}@{v}'.format(n=name, v=version)
            path = os.path.join(e.path, name)
            manager('develop', '--repo-branch', repo, branch, spec)
            mock_develop.assert_called_once()
            mock_git_clone.assert_called_once_with(branch, repo, path, False)
