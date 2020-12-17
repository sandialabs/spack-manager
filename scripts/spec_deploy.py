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
uninstall = SpackCommand('uninstall')

def check_for_env(env_name):
    if env_name not in env('ls'):
        raise Exception(
           'Environment {env} has not been created'.format(env=env_name))


def uninstall_spec_from_env(env_name, spec_name):
    my_env = spenv.Environment(env_name)
    if my_env.active():
        my_env.deactivate()
    uninstall('-f', spec_name)

def SpecEnvDeploy(env_name, spec_name):
    check_for_env(env_name)

    uninstall_spec_from_env(env_name, spec_name)

    with spenv.read(env_name):
        print(install('-y','-v','{spec}'.format(spec=spec_name)))
        env('loads', '-r')
    CreateUserLoads(env_name)

if __name__ == '__main__':
    env_name = sys.argv[1]
    spec_name = " ".join(sys.argv[2:])
    SpecEnvDeploy(env_name, spec_name)
