from tempfile import TemporaryDirectory
import filecmp
import os
import create_machine_spack_environment as cmse
import pytest


def test_basicDirectoryProperties():
    with TemporaryDirectory() as tmpdir:
        args = cmse.parse(['-d', tmpdir, '-m', 'darwin', '-s', 'binutils'])
        assert filecmp.dircmp(tmpdir, args.directory)
        assert 'darwin' == args.machine
        cmse.CreateEnvDir(args)
        assert os.path.isfile(os.path.join(tmpdir, 'machine_config.yaml'))


def test_failsWithAnUnregisteredMachine():
    with TemporaryDirectory as tmpdir:
        args = cmse.parse(['-d', tmpdir, '-m', 'theGOAT_HPC'])

        with pytest.raises(AttributeError) as einfo:
            cmse.CreateEnvDir(args)

        assert 'Host not setup in spack-manager' in str(einfo.value)
