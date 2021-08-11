#!/usr/bin/env spack-python
"""
A script for creating a new environment
on a given machine
"""

import shutil
import os
from find_machine import find_machine

default_env_file = (
 """spack:
  include:
  - general_packages.yaml
  - general_config.yaml
  - general_repos.yaml
  - machine_config.yaml
  - machine_packages.yaml
  - machine_compilers.yaml
  concretization: together
  specs:
  - {spec}""")

def NewName(newHead, oldFile, prefix=None):
    tail = os.path.basename(oldFile)
    print(oldFile, tail, newHead)
    if prefix is not None:
        return os.path.join(newHead, prefix + '_' + tail)
    else:
        return os.path.join(newHead, tail)

def CopyFilesAcrossPaths(pathStart, pathEnd, prefix=None):
    for f in os.listdir(pathStart):
        d = os.path.join(pathStart, f)
        shutil.copy(d, NewName(pathEnd, d, prefix))

def CreateEnvDir(args):
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

        CopyFilesAcrossPaths(genPath, theDir, 'general')

        CopyFilesAcrossPaths(hostPath, theDir, 'machine')

        if args.yaml is not None:
            assert(os.path.isfile(args.yaml))
            shutil.copy(args.yaml, os.path.join(theDir, 'spack.yaml'))
        else:
            open(os.path.join(theDir, 'spack.yaml'),'w').write(default_env_file.format(spec=spec))
    else:
        raise Exception('Host not setup in spack-manager: %s' % hostPath)

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description=
        'A convenience script for setting up a spack environment through the spack-manager repository.')
    parser.add_argument('-m', '--machine', required=False, help='Machine to match configs')
    parser.add_argument('-d', '--directory', required=False, help='Directory to copy files')
    parser.add_argument('-y', '--yaml', required=False, help='Reference spack.yaml to copy to directory')
    parser.add_argument('-s', '--spec', required=False, help='Spec to populate the environment with')
    args = parser.parse_args()
    CreateEnvDir(args)
