# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

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


def test_specsCanBeAddedToExisitingYaml(tmpdir):
    with tmpdir.as_cwd():
        preset_yaml = """
spack:
  develop:
    amr-wind:
      spec: amr-wind@main
      path: /tst/dir"""

        with open('test.yaml', 'w') as fyaml:
            fyaml.write(preset_yaml)

        env_root = str(tmpdir.join('dev'))
        os.makedirs(env_root)

        assert os.path.isfile('test.yaml')
        manager('create-env', '-d', env_root, '-m', 'darwin',
                '-y', 'test.yaml', '-s', 'amr-wind', 'nalu-wind')

        e = env.Environment(env_root)
        assert e.yaml['spack']['specs'][0] == 'amr-wind'
        assert e.yaml['spack']['specs'][1] == 'nalu-wind'
        assert e.yaml['spack']['develop']['amr-wind']['spec'] == 'amr-wind@main'
        assert e.yaml['spack']['develop']['amr-wind']['path'] == '/tst/dir'
        assert not e.yaml['spack']['view']


def test_existingYamlViewIsNotOverwritten(tmpdir):
    with tmpdir.as_cwd():
        preset_yaml = """
spack:
  view: true
  develop:
    amr-wind:
      spec: amr-wind@main
      path: /tst/dir"""

        with open('test.yaml', 'w') as fyaml:
            fyaml.write(preset_yaml)

        env_root = str(tmpdir.join('dev'))
        os.makedirs(env_root)

        assert os.path.isfile('test.yaml')

        manager('create-env', '-d', env_root, '-m', 'darwin',
                '-y', 'test.yaml', '-s', 'amr-wind', 'nalu-wind')

        e = env.Environment(env_root)
        assert e.yaml['spack']['view']


def test_specs_can_have_spaces(tmpdir):
    with tmpdir.as_cwd():
        manager('create-env',
                '-s', 'nalu-wind', 'build_type=Release', '%gcc')
