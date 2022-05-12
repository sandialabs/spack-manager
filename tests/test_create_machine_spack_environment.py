#!/usr/bin/env spack-python
# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from tempfile import TemporaryDirectory
import filecmp
import os
import create_machine_spack_environment as cmse
import pytest


def test_basicDirectoryProperties():
    with TemporaryDirectory() as tmpdir:
        args = cmse.Parse(['-d', tmpdir, '-m', 'darwin', '-s', 'binutils'])
        assert filecmp.dircmp(tmpdir, args.directory)
        assert 'darwin' == args.machine
        cmse.CreateEnvDir(args)
        assert os.path.isfile(os.path.join(tmpdir, 'general_packages.yaml'))


def test_failsWithAnUnregisteredMachine():
    with TemporaryDirectory() as tmpdir:
        args = cmse.Parse(['-d', tmpdir, '-m', 'theGOAT_HPC'])
        pytest.raises(Exception, cmse.CreateEnvDir, args)


TESTMACHINE = 'test_machine'


def test_missingSourceFilesDontBreakEnv(monkeypatch):
    with TemporaryDirectory() as tmpdir:
        # setup a mirror configuration of spack-manager
        link_dir = os.path.join(os.environ['SPACK_MANAGER'], 'configs', 'base')

        os.mkdir(os.path.join(tmpdir, 'configs'))
        os.symlink(link_dir,
                   os.path.join(tmpdir, 'configs', 'base'))
        os.mkdir(os.path.join(tmpdir, 'configs', TESTMACHINE))

        # monkeypatches
        envVars = {'SPACK_MANAGER': tmpdir}
        monkeypatch.setattr(os, 'environ', envVars)

        def MockFindMachine():
            return TESTMACHINE

        monkeypatch.setattr(cmse, 'find_machine', MockFindMachine)

        # create spack.yaml
        args = cmse.Parse(['-d', tmpdir])
        cmse.CreateEnvDir(args)

        # ideally I'd just try to activate the spack env, but I haven't
        # figures out good way yet.  Adding spack to PYTHONPATH introduces
        # a bunch of non-standard module dependencies
        with open(os.path.join(tmpdir, 'spack.yaml'), 'r') as spackYaml:
            # verify that no machine yamls are in file
            for line in spackYaml:
                assert ('machine' not in line)
                assert ('-' in line) if 'general' in line else True
