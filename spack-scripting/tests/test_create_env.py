import os
from tempfile import TemporaryDirectory

import manager_cmds.create_env as create_env
import pytest

import spack.environment as env
import spack.main

manager = spack.main.SpackCommand('manager')
envcmd = spack.main.SpackCommand('env')


def test_basicDirectoryProperties():
    with TemporaryDirectory() as tmpdir:
        manager('create-env', '-d', tmpdir, '-m', 'darwin', '-s', 'binutils')
        assert os.path.isfile(os.path.join(tmpdir, 'spack.yaml'))
        assert os.path.isfile(os.path.join(tmpdir, 'include.yaml'))


def test_failsWithAnUnregisteredMachine():
    with TemporaryDirectory() as tmpdir:
        with pytest.raises(Exception):
            manager('create-env', '-d', tmpdir, '-m', 'theGOAT_HPC')


def test_missingReferenceYamlFilesDontBreakEnv(monkeypatch):
    TESTMACHINE = 'test_machine'
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

        def MockFindMachine(verbose=True):
            if verbose:
                print(TESTMACHINE)
            return TESTMACHINE

        monkeypatch.setattr(create_env, 'find_machine', MockFindMachine)

        # create spack.yaml
        manager('create-env', '-d', tmpdir)

        # ensure that this environment can be created
        # missing includes will cause a failure
        env.Environment(tmpdir)
