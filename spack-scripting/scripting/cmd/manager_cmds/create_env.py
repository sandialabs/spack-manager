
"""
A script for creating a new environment
on a given machine
"""

import argparse
import os
import shutil

import manager_cmds.find_machine as fm
from manager_cmds.find_machine import find_machine
from manager_cmds.includes_creator import IncludesCreator

import spack.cmd.env as envcmd
import spack.util.spack_yaml as syaml

default_env_file = (
    """
spack:
  include: []
  concretization: together
  view: false
  specs: []""")


def create_env(parser, args):
    yaml = syaml.load_config(default_env_file)
    if args.machine is not None:
        machine = args.machine
        if machine not in fm.machine_list.keys():
            raise Exception('Specified machine %s is not defined' % machine)
    else:
        machine = find_machine(verbose=(not args.activate))

    if args.spec:
        yaml['spack']['specs'] = args.spec

    inc_creator = IncludesCreator()
    genPath = os.path.join(os.environ['SPACK_MANAGER'], 'configs', 'base')
    inc_creator.add_scope('base', genPath)
    hostPath = os.path.join(os.environ['SPACK_MANAGER'], 'configs', machine)

    if os.path.exists(hostPath):
        inc_creator.add_scope('machine', hostPath)
    else:
        if not args.activate:
            print('Host not setup in spack-manager: %s' % hostPath)

    if args.directory is not None:
        if os.path.exists(args.directory) is False:
            if not args.activate:
                print("making", args.directory)
            os.makedirs(args.directory)

        theDir = args.directory
    elif args.name is not None:
        theDir = os.path.join(
            os.environ['SPACK_MANAGER'], 'environments', args.name)
        if os.path.exists(theDir) is False:
            if not args.activate:
                print("making", theDir)
            os.makedirs(theDir)
    else:
        theDir = os.getcwd()

    include_file_name = 'include.yaml'
    include_file = os.path.join(theDir, include_file_name)
    inc_creator.write_includes(include_file)
    yaml['spack']['include'].append(include_file_name)

    if args.yaml is not None:
        assert(os.path.isfile(args.yaml))
        shutil.copy(args.yaml, os.path.join(theDir, 'spack.yaml'))
    else:
        with open(os.path.join(theDir, 'spack.yaml'), 'w') as f:
            syaml.dump_config(yaml, stream=f, default_flow_style=False)

    if args.activate:
        dumb_parser = argparse.ArgumentParser('dummy')
        dumb_parser.add_argument('-env', required=False)
        dumb_parser.add_argument('-no-env', required=False)
        dumb_parser.add_argument('-env-dir', required=False)
        envcmd.env_activate_setup_parser(dumb_parser)
        activate_args = dumb_parser.parse_args(['-d', theDir, '-p', '--sh'])
        envcmd.env_activate(activate_args)
    return theDir


def setup_parser_args(sub_parser):
    sub_parser.add_argument('-m', '--machine', required=False,
                            help='Machine to match configs')
    name_group = sub_parser.add_mutually_exclusive_group()
    name_group.add_argument('-d', '--directory', required=False,
                            help='Directory to copy files')
    name_group.add_argument('-n', '--name', required=False,
                            help='Name of directory to copy files that will be in '
                            '$SPACK_MANAGER/environments')
    sub_parser.add_argument('-y', '--yaml', required=False,
                            help='Reference spack.yaml to copy to directory')
    sub_parser.add_argument('-s', '--spec', required=False, default=[], nargs='+',
                            help='Specs to populate the environment with')
    sub_parser.add_argument('-a', '--activate', dest='activate', required=False,
                            action='store_true', default=False,
                            help='Print the shell script required to activate '
                            'the environment upon creation. '
                            'When called with swspack it will auto activate'
                            ' the env')


def add_command(parser, command_dict):
    sub_parser = parser.add_parser('create-env', help='convenience script'
                                   ' for setting up a spack environment')
    setup_parser_args(sub_parser)
    command_dict['create-env'] = create_env
