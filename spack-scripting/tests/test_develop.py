# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

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
    @patch('manager_cmds.develop.git_remote_add')
    @pytest.mark.parametrize('all_branches', [True, False])
    @pytest.mark.parametrize('shallow', [True, False])
    @pytest.mark.parametrize('add_remote', [True, False])
    def test_spackManagerExtensionArgsLeadToGitCalls(
            self, mock_git_remote, mock_git_clone, mock_develop,
            all_branches, shallow, add_remote):
        env('create', 'test')
        with ev.read('test') as e:
            branch = 'master'
            repo = 'https://a.git.repo'
            name = 'mpich'
            version = '1.0'
            spec = '{n}@{v}'.format(n=name, v=version)
            path = os.path.join(e.path, name)
            manager_args = ['develop', '--repo-branch', repo, branch]
            if all_branches:
                manager_args.append('--all-branches')
            if shallow:
                manager_args.append('--shallow')
            if add_remote:
                remote_name = 'foo'
                remote_repo = 'https://b.git.repo'
                manager_args.extend(
                    ['--add-remote', remote_name, remote_repo])
            manager_args.append(spec)
            manager(*manager_args)
            mock_develop.assert_called_once()
            mock_git_clone.assert_called_once_with(
                branch, repo, path, shallow, all_branches)
            if add_remote:
                mock_git_remote.assert_called_once_with(
                    path, remote_name, remote_repo)
            else:
                assert not mock_git_remote.called
