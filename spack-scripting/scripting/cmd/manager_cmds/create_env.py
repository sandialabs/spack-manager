
"""
A script for creating a new environment
on a given machine
"""

import os
import shutil

from find_machine import find_machine

default_env_file = (
    """
spack:
  include:
{includes}
  concretization: together
  view: false
  specs:
  - {spec}""")


def create_includes(master_file, path_ref_files):
    with open(master_file, 'wb') as fm:
        for f in os.listdir(path_ref_files):
            with open(os.path.abspath(os.path.join(path_ref_files, f)), 'rb') as fs:
                shutil.copyfileobj(fs, fm)


def create_env(parser, args):
    """
    Copy files as needed
    """
    if args.machine is not None:
        machine = args.machine
    else:
        machine = find_machine()

    if args.spec is not None:
        spec = args.spec
    else:
        # give a blank spec
        spec = ''

    genPath = os.path.join(os.environ['SPACK_MANAGER'], 'configs', 'base')
    hostPath = os.path.join(os.environ['SPACK_MANAGER'], 'configs', machine)

    if os.path.exists(hostPath):
        if args.directory is not None:
            if os.path.exists(args.directory) is False:
                print("making", args.directory)
                os.makedirs(args.directory)

            theDir = args.directory
        else:
            theDir = os.getcwd()

        include_file_name = 'include.yaml'
        include_file = os.path.join(theDir, include_file_name)
        create_includes(include_file, hostPath)
        create_includes(include_file, genPath)

        include_str = '  - {v}\n'.format(v=include_file_name)

        if args.yaml is not None:
            assert(os.path.isfile(args.yaml))
            shutil.copy(args.yaml, os.path.join(theDir, 'spack.yaml'))
        else:
            open(os.path.join(theDir, 'spack.yaml'), 'w').write(
                default_env_file.format(spec=spec, includes=include_str))
    else:
        raise Exception('Host not setup in spack-manager: %s' % hostPath)


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
