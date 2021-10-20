from tempfile import TemporaryDirectory
import filecmp
import os
import create_machine_spack_environment as cmse


def test_basicDirectoryProperties():
    with TemporaryDirectory() as tmpdir:
        args = cmse.parse(['-d', tmpdir, '-m', 'darwin', '-s', 'binutils'])
        assert filecmp.dircmp(tmpdir, args.directory)
        assert 'darwin' == args.machine
        cmse.CreateEnvDir(args)
        assert os.path.isfile(os.path.join(tmpdir, 'machine_config.yaml'))

