
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


def NewName(newHead, oldFile, prefix=None):
    tail = os.path.basename(oldFile)
    if prefix is not None:
        return os.path.join(newHead, prefix + '_' + tail)
    else:
        return os.path.join(newHead, tail)


def CopyFilesAcrossPaths(pathStart, pathEnd, prefix=None):
    copiedFiles = []
    for f in os.listdir(pathStart):
        d = os.path.join(pathStart, f)
        n = NewName(pathEnd, d, prefix)
        copiedFiles.append(os.path.basename(n))
        shutil.copy(d, n)
    return copiedFiles


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
        spec = 'exawind'

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

        machineFiles = CopyFilesAcrossPaths(hostPath, theDir, 'machine')
        generalFiles = CopyFilesAcrossPaths(genPath, theDir, 'general')

        includeString = ''
        for x in machineFiles + generalFiles:
            includeString += '  - {v}\n'.format(v=x)

        if args.yaml is not None:
            assert(os.path.isfile(args.yaml))
            shutil.copy(args.yaml, os.path.join(theDir, 'spack.yaml'))
        else:
            open(os.path.join(theDir, 'spack.yaml'), 'w').write(
                default_env_file.format(spec=spec, includes=includeString))
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
