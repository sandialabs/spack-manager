#!/usr/bin/env spack-python
from spack.main import SpackCommand
import spack.environment as spenv
import pathlib
import sys
import os

script_loc = os.path.join(os.environ['SPACK_MANAGER'],'scripts')
sys.path.append(script_loc)

from create_load_script import CreateUserLoads

install = SpackCommand('install')
env = SpackCommand('env')

def SpecEnvDeploy(env_name, spec_name):
    if env_name not in env('ls'):
        print('Environment {env} has not been created'.format(env=env_name))
        exit(10)

    with spenv.read(env_name):
        print(install('--overwrite','-y','-v','{spec}'.format(spec=spec_name)))
        env('view','enable')
        env('view', 'loads', '-r')
    CreateUserLoads(env_name)

if __name__ == '__main__':
    env_name = sys.argv[1]
    spec_name = " ".join(sys.argv[2:])
    SpecEnvDeploy(env_name, spec_name)
