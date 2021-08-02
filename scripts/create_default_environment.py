#!/usr/bin/env spack-python
"""
A script for creating a new environment
on a given machine
"""

import shutil
import os

default_env_file =
 r'spack:
  include:
  - general_packages.yaml
  - general_module_view_pair.yaml
  - general_repos.yaml
  - machine_config.yaml
  - machine_packages.yaml
  - machine_compilers.yaml
  - machine_general.yaml
  specs:
  - exawind'

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
    genPath = os.path.join(os.environ['SPACK_MANAGER'], 'configs', 'base')
    hostPath = os.path.join(os.environ['SPACK_MANAGER'], 'configs', args.machine)

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

        if os.path.exists(args.spack_yaml):
            shutil.copy(args.spack_yaml, os.path.join(theDir, 'spack.yaml'))
        else:
            open(os.path.join.theDir, 'spack.yaml','w').write(default_env_file)
    else:
        raise Exception('Host not setup in spack-manager: %s' % hostPath)

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description=
        'Copy machine files to a diectory for creating an environment')
    parser.add_argument('-m', '--machine', required=True, help='Machine to match configs')
    parser.add_argument('-d', '--directory', required=False, help='Directory to copy files')
    parser.add_argument('-s', '--spack_yaml', required=False, help='Reference spack.yaml to copy to directory')
    args = parser.parse_args()
    CreateEnvDir(args)
