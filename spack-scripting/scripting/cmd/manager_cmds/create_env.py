
"""
A script for creating a new environment
on a given machine
"""

import os
import shutil

import manager_cmds.find_machine as fm
from manager_cmds.find_machine import find_machine
from manager_cmds.includes_creator import IncludesCreator

default_env_file = (
    """
spack:
  include:
{includes}
  concretization: together
  view: false
  specs:
  - {spec}""")


def create_env(parser, args):
    """
    Copy files as needed
    """
    if args.machine is not None:
        machine = args.machine
        if machine not in fm.machine_list.keys():
            raise Exception('Specified machine %s not defined' % machine)
    else:
        machine = find_machine()

    if args.spec is not None:
        spec = args.spec
    else:
        # give a blank spec
        spec = ''

    inc_creator = IncludesCreator()
    genPath = os.path.join(os.environ['SPACK_MANAGER'], 'configs', 'base')
    inc_creator.add_scope('base', genPath)
    hostPath = os.path.join(os.environ['SPACK_MANAGER'], 'configs', machine)

    if os.path.exists(hostPath):
        inc_creator.add_scope('machine', hostPath)
    else:
        print('Warning: pre-configured'
              ' machine not setup in spack-manager: %s' % machine)

    if args.directory is not None:
        if os.path.exists(args.directory) is False:
            print("making", args.directory)
            os.makedirs(args.directory)

        theDir = args.directory
    else:
        theDir = os.getcwd()

    include_file_name = 'include.yaml'
    include_file = os.path.join(theDir, include_file_name)
    inc_creator.write_includes(include_file)

    include_str = '  - {v}\n'.format(v=include_file_name)

    if args.yaml is not None:
        assert(os.path.isfile(args.yaml))
        shutil.copy(args.yaml, os.path.join(theDir, 'spack.yaml'))
    else:
        open(os.path.join(theDir, 'spack.yaml'), 'w').write(
            default_env_file.format(spec=spec, includes=include_str))


def add_command(parser, command_dict):
    sub_parser = parser.add_parser('create-env', help='convenience script'
                                   ' for setting up a spack environment')
    sub_parser.add_argument('-m', '--machine', required=False,
                            help='Machine to match configs')
    sub_parser.add_argument('-d', '--directory', required=False,
                            help='Directory to copy files')
    sub_parser.add_argument('-y', '--yaml', required=False,
                            help='Reference spack.yaml to copy to directory')
    sub_parser.add_argument('-s', '--spec', required=False,
                            help='Spec to populate the environment with')
    command_dict['create-env'] = create_env
