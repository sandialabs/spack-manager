#!/usr/bin/env spack-python
import llnl.util.tty as tty
tty.set_debug(False)
tty.set_timestamp(True)
from spack.main import SpackCommand
import spack.environment as env
import pathlib
import sys
import os
import spack.util.executable

script_loc = os.path.join(os.environ['SPACK_MANAGER'],'scripts')
sys.path.append(script_loc)

from create_load_script import CreateUserLoads

env_cmd = SpackCommand('env')
cd = SpackCommand('cd')
git = spack.util.executable.which('git')

def SpecEnvDeploy(env_name):
    """Pull all develop branches and then reinstall"""
    if env.exists(env_name):
        this_env = env.read(env_name)
        with this_env:
            for name, entry in this_env.dev_specs.items():
                print(name)
                cd(name)
                try:
                    git('fetch', '--unshallow')
                except:
                    pass
                git('pull')
                git('submodule', 'update')
            this_env.install_all()
            env_cmd('loads', '-r')
        CreateUserLoads(env_name)
    else:
        raise Exception(
           'Environment {env} has not been created'.format(env=env_name))


if __name__ == '__main__':
    env_name = sys.argv[1]
    SpecEnvDeploy(env_name)
