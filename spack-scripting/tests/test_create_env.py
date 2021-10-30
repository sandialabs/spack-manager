from tempfile import TemporaryDirectory
import os
import manager_cmds.create_env as create_env
import spack.main
import spack.environment as env
import pytest

manager = spack.main.SpackCommand('manager')


def test_basicDirectoryProperties():
    with TemporaryDirectory() as tmpdir:
        manager('create-env','-d', tmpdir, '-m', 'darwin', '-s', 'binutils')
        assert os.path.isfile(os.path.join(tmpdir, 'spack.yaml'))
        assert os.path.isfile(os.path.join(tmpdir, 'general_packages.yaml'))


def test_failsWithAnUnregisteredMachine():
    with TemporaryDirectory() as tmpdir:
        with pytest.raises(Exception):
            manager('create-env','-d', tmpdir, '-m', 'theGOAT_HPC')


TESTMACHINE = 'test_machine'


def test_missingReferenceYamlFilesDontBreakEnv(monkeypatch):
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

        monkeypatch.setattr(create_env, 'find_machine', MockFindMachine)

        # create spack.yaml
        manager('create-env', '-d', tmpdir)

        # ensure that this environment can be created
        # missing includes will cause a failure
        env.Environment(tmpdir)