#! /usr/bin/env spack-python

import os
import argparse
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


parser = argparse.ArgumentParser(
    'Run a test of the developer snapshot workflow')
parser.add_argument('--view_name', required=False,
                    help='view to use for the developer')
parser.add_argument('--snap_name', required=False,
                    help='directory name for the snapshot')
parser.add_argument('--dev_name', required=False,
                    help='directory name for the developer env')
parser.add_argument('--num_threads', required=False,
                    help='DAG paralleization')
parser.set_defaults(view_name='default', snap_name='test',
                    dev_name='test_external', num_threads=1)
args = parser.parse_args()

# set up the snapshot
print('Create Snapshot')
args = snapshot_creator.parse(
    ['--use_develop', '--modules', '--name', args.snap_name,
     '--num_threads', args.num_threads])
snapshot_path = snapshot_creator.create_snapshots(args)
print('Snapshot created at', snapshot_path)

# set up the user environment
ev.deactivate()
env_path = os.path.join(os.environ['SPACK_MANAGER'],
                        'environments', args.dev_name)
command(manager, 'create-env', '--directory', env_path, '--spec', 'nalu-wind')
ev.activate(ev.Environment(env_path))
command(config, 'add', 'config:concretizer:original')
command(manager, 'external', snapshot_path, '-v', args.view_name,
        '--blacklist', 'nalu-wind')
command(manager, 'develop', 'nalu-wind@master')
command(concretize)
command(install)
