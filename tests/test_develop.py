# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

import os
import pytest

import spack.environment as ev
import spack.extensions
import spack.extensions.manager.manager_cmds.develop as m_develop
import spack.main

env = spack.main.SpackCommand("env")
manager = spack.main.SpackCommand("manager")

@pytest.mark.usefixtures("mock_packages", "mock_fetch")
def test_spackManagerDevelopCallsSpackDevelop(monkeypatch, arg_capture, tmpdir):
    eDir = tmpdir.join("test")
    env("create" "-d", eDir)
    with ev.read(eDir):
        monkeypatch.setattr(m_develop, "s_develop", arg_capture)
        manager("develop", "mpich@=1.0")
        assert arg_capture.num_calls == 1

@pytest.mark.usefixtures("mutable_mock_env_path", "mock_packages", "mock_fetch")
@pytest.mark.parametrize("all_branches", [True, False])
@pytest.mark.parametrize("shallow", [True, False])
@pytest.mark.parametrize("add_remote", [True, False])
def test_spackManagerExtensionArgsLeadToGitCalls(
    tmpdir, monkeypatch, arg_capture_patch, all_branches, shallow, add_remote
):
    mock_develop = arg_capture_patch()
    mock_git_clone = arg_capture_patch()
    mock_git_remote = arg_capture_patch()
    monkeypatch.setattr(m_develop, "s_develop", mock_develop)
    monkeypatch.setattr(m_develop, "git_clone", mock_git_clone)
    monkeypatch.setattr(m_develop, "git_remote_add", mock_git_remote)
    eDir = tmpdir.join("test")
    env("create", "-d", eDir)
    with ev.read(eDir) as e:
        branch = "master"
        repo = "https://a.git.repo"
        name = "mpich"
        version = "1.0"
        spec = "{n}@={v}".format(n=name, v=version)
        path = os.path.join(e.path, name)
        manager_args = ["develop", "--repo-branch", repo, branch]
        if all_branches:
            manager_args.append("--all-branches")
        if shallow:
            manager_args.append("--shallow")
        if add_remote:
            remote_name = "foo"
            remote_repo = "https://b.git.repo"
            manager_args.extend(["--add-remote", remote_name, remote_repo])
        manager_args.append(spec)
        manager(*manager_args)
        assert mock_develop.num_calls == 1
        mock_git_clone.assert_call_matches(1, [branch, repo, path, shallow, all_branches])
        if add_remote:
            mock_git_remote.assert_call_matches(1, [path, remote_name, remote_repo])
        else:
            assert not bool(mock_git_remote.num_calls)
