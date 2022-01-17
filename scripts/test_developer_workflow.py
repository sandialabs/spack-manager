#! /usr/bin/env spack-python

import os
import spack.main
import spack.environment as ev
import snapshot_creator

manager = spack.main.SpackCommand('manager')
concretize = spack.main.SpackCommand('concretize')
config = spack.main.SpackCommand('config')
install = spack.main.SpackCommand('install')


def command(command, *args):
    print('spack', command.command_name, *args)
    print(command(*args, fail_on_error=False))


# set up the snapshot
print('Create Snapshot')
args = snapshot_creator.parse(['--use_develop', '--modules', '--name', 'test'])
snapshot_creator.create_snapshots(args)
snapshot_path = os.path.join(os.environ['SPACK_MANAGER'],
                             'environments/exawind/snapshots/skylake/test')
print('Snapshot created at', snapshot_path)

# set up the user environment
env_path = os.path.join(os.environ['SPACK_MANAGER'],
                        'environments/test_externals')
command(manager, 'create-env', '--directory', env_path, '--spec', 'nalu-wind')
ev.activate(ev.Environment(env_path))
command(config, 'add', 'config:concretizer:original')
command(manager, 'external', snapshot_path, '--blacklist', 'nalu-wind')
command(manager, 'develop', 'nalu-wind@master')
command(concretize)
command(install)
