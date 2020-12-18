#!/usr/bin/env spack-python
from spack.main import SpackCommand
import spack.environment as env
import pathlib
import sys
import os
import spack.executable

script_loc = os.path.join(os.environ['SPACK_MANAGER'],'scripts')
sys.path.append(script_loc)

from create_load_script import CreateUserLoads

env_cmd = SpackCommand('env')
cd = SpackCommand('cd')
git = spack.executable.which('git')

def SpecEnvDeploy(env_name):
    """Pull all develop branches and then reinstall"""
    if env.exists(env_name):
        this_env = env.find_environment(env_name)
        with this_env:
            for root in this_env.roots():
                # roots should only be develop specs, need to add check
                cd(r.name)
                git('pull')
            this_env.concretize()
            this_env.install_all()
            env_cmd('loads', '-r')
        CreateUserLoads(env_name)
    else:
        raise Exception(
           'Environment {env} has not been created'.format(env=env_name))


if __name__ == '__main__':
    env_name = sys.argv[1]
    SpecEnvDeploy(env_name)
